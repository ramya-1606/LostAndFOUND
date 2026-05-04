import os
import uuid
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, g
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'college-lost-found-secret-key'
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'lostandfound.db')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()

def init_db():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS item (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                type          TEXT NOT NULL,
                title         TEXT NOT NULL,
                description   TEXT NOT NULL,
                category      TEXT NOT NULL,
                location      TEXT NOT NULL,
                date_reported TEXT NOT NULL,
                contact_name  TEXT NOT NULL,
                contact_info  TEXT NOT NULL,
                image_filename TEXT,
                status        TEXT NOT NULL DEFAULT 'open',
                edit_token    TEXT NOT NULL
            )
        """)
        db.commit()

def row_to_dict(row):
    d = dict(row)
    dt = datetime.strptime(d['date_reported'], '%Y-%m-%d %H:%M:%S')
    delta = datetime.utcnow() - dt
    if delta.days > 0:
        d['time_ago'] = f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
    elif delta.seconds // 3600 > 0:
        h = delta.seconds // 3600
        d['time_ago'] = f"{h} hour{'s' if h != 1 else ''} ago"
    else:
        m = max(delta.seconds // 60, 1)
        d['time_ago'] = f"{m} minute{'s' if m != 1 else ''} ago"
    d['date_display'] = dt.strftime('%B %d, %Y at %I:%M %p')
    return d

CATEGORIES = [
    'Electronics', 'Clothing & Accessories', 'ID Cards & Documents',
    'Keys', 'Bags & Wallets', 'Books & Stationery', 'Sports Equipment', 'Other'
]
LOCATIONS = [
    'Main Library', 'Cafeteria', 'Auditorium', 'Sports Complex',
    'Lecture Block A', 'Lecture Block B', 'Lab Block', 'Hostel',
    'Parking Lot', 'Admin Block', 'Other'
]
CAT_EMOJI = {
    'Electronics': '📱', 'Clothing & Accessories': '👗',
    'ID Cards & Documents': '🪪', 'Keys': '🔑',
    'Bags & Wallets': '👝', 'Books & Stationery': '📚',
    'Sports Equipment': '⚽', 'Other': '📦'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    img = Image.open(file)
    img.thumbnail((800, 800))
    img.save(path)
    return unique_name

@app.route('/')
def index():
    return "APP IS RUNNING"
        recent_lost=recent_lost, recent_found=recent_found,
        total_open=total_open, total_resolved=total_resolved, cat_emoji=CAT_EMOJI)

@app.route('/items')
def items():
    db = get_db()
    item_type = request.args.get('type', '')
    category  = request.args.get('category', '')
    location  = request.args.get('location', '')
    search    = request.args.get('search', '')
    status    = request.args.get('status', 'open')

    sql, params = "SELECT * FROM item WHERE 1=1", []
    if item_type: sql += " AND type=?";     params.append(item_type)
    if category:  sql += " AND category=?"; params.append(category)
    if location:  sql += " AND location=?"; params.append(location)
    if status:    sql += " AND status=?";   params.append(status)
    if search:
        sql += " AND (title LIKE ? OR description LIKE ?)"; params += [f'%{search}%', f'%{search}%']
    sql += " ORDER BY date_reported DESC"

    results = [row_to_dict(r) for r in db.execute(sql, params).fetchall()]
    return render_template('items.html',
        items=results, categories=CATEGORIES, locations=LOCATIONS,
        current_type=item_type, current_category=category,
        current_location=location, current_search=search, current_status=status,
        cat_emoji=CAT_EMOJI)

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    db  = get_db()
    row = db.execute("SELECT * FROM item WHERE id=?", (item_id,)).fetchone()
    if not row: abort(404)
    item     = row_to_dict(row)
    token    = request.args.get('token', '')
    is_owner = token == item['edit_token']
    return render_template('item_detail.html',
        item=item, is_owner=is_owner, token=token, cat_emoji=CAT_EMOJI)

@app.route('/post', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
        title        = request.form.get('title', '').strip()
        description  = request.form.get('description', '').strip()
        item_type    = request.form.get('type', '')
        category     = request.form.get('category', '')
        location     = request.form.get('location', '')
        contact_name = request.form.get('contact_name', '').strip()
        contact_info = request.form.get('contact_info', '').strip()

        if not all([title, description, item_type, category, location, contact_name, contact_info]):
            flash('Please fill in all required fields.', 'error')
            return render_template('post.html', categories=CATEGORIES, locations=LOCATIONS)

        image_filename = None
        file = request.files.get('image')
        if file and file.filename and allowed_file(file.filename):
            image_filename = save_image(file)

        token = str(uuid.uuid4())
        now   = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        db    = get_db()
        cur   = db.execute(
            """INSERT INTO item (type,title,description,category,location,date_reported,
               contact_name,contact_info,image_filename,status,edit_token)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (item_type, title, description, category, location, now,
             contact_name, contact_info, image_filename, 'open', token))
        db.commit()
        flash('Your item has been posted! Bookmark this page to resolve it later.', 'success')
        return redirect(url_for('item_detail', item_id=cur.lastrowid, token=token))

    return render_template('post.html', categories=CATEGORIES, locations=LOCATIONS)

@app.route('/item/<int:item_id>/resolve', methods=['POST'])
def resolve_item(item_id):
    db  = get_db()
    row = db.execute("SELECT * FROM item WHERE id=?", (item_id,)).fetchone()
    if not row: abort(404)
    if request.form.get('token','') != row['edit_token']: abort(403)
    db.execute("UPDATE item SET status='resolved' WHERE id=?", (item_id,))
    db.commit()
    flash('Item marked as resolved. Happy it worked out! 🎉', 'success')
    return redirect(url_for('item_detail', item_id=item_id))

@app.route('/item/<int:item_id>/reopen', methods=['POST'])
def reopen_item(item_id):
    db  = get_db()
    row = db.execute("SELECT * FROM item WHERE id=?", (item_id,)).fetchone()
    if not row: abort(404)
    token = request.form.get('token','')
    if token != row['edit_token']: abort(403)
    db.execute("UPDATE item SET status='open' WHERE id=?", (item_id,))
    db.commit()
    flash('Item reopened.', 'success')
    return redirect(url_for('item_detail', item_id=item_id, token=token))

from flask import Flask
import os

app = Flask(__name__)

# ✅ Initialize DB safely (Flask 3 compatible)
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print("DB init error:", e)
    