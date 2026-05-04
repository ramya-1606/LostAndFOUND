"""Seed demo data. Run once: python seed.py"""
import sqlite3, uuid, os
from datetime import datetime, timedelta

DB = os.path.join(os.path.dirname(__file__), 'lostandfound.db')
os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'uploads'), exist_ok=True)

con = sqlite3.connect(DB)
con.execute("""CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, title TEXT NOT NULL,
    description TEXT NOT NULL, category TEXT NOT NULL, location TEXT NOT NULL,
    date_reported TEXT NOT NULL, contact_name TEXT NOT NULL, contact_info TEXT NOT NULL,
    image_filename TEXT, status TEXT NOT NULL DEFAULT 'open', edit_token TEXT NOT NULL)""")

def ts(hours_ago=0, days_ago=0):
    return (datetime.utcnow() - timedelta(hours=hours_ago, days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

samples = [
    ('lost',  'Black Dell Laptop Bag', 'Bags & Wallets',    'Main Library',    'Black Dell laptop bag with a red zip tag. Contains charger and notebook. Lost near the reading section on the 2nd floor.', 'Arjun K.',   'arjun.k@college.edu', ts(hours_ago=3)),
    ('found', 'Bunch of Keys with Blue Keychain', 'Keys',   'Cafeteria',       'Found a bunch of keys with a small blue rubber duck keychain near the food counter. About 4-5 keys on the ring.', 'Meera S.',   '9876501234',          ts(hours_ago=7)),
    ('lost',  'College ID Card — Rohit Verma', 'ID Cards & Documents', 'Sports Complex', 'Lost my college ID and library card together in a small card sleeve. Blue and white college design. Please contact ASAP.', 'Rohit V.',   'rohit.v@college.edu', ts(days_ago=1)),
    ('found', 'Casio Digital Watch (Silver)', 'Electronics', 'Lecture Block A', 'Found a silver Casio digital watch on the bench outside room A-204. Looks like it was left behind after class.', 'Divya R.',   '9988776655',          ts(days_ago=1, hours_ago=4)),
    ('lost',  'Maths Textbook + Notes Bundle', 'Books & Stationery', 'Lecture Block B', 'Lost a thick Engineering Mathematics textbook (3rd edition) with handwritten notes tucked inside. My name is written on the first page.', 'Sana P.',    'sana.p@college.edu',  ts(days_ago=2)),
    ('found', 'Pink boAt Earphones', 'Electronics',          'Hostel',          'Found pink boAt earphones near the hostel common room. They were on the window sill. Please describe them to claim.', 'Lakshmi T.', '9000011112',          ts(hours_ago=12)),
    ('lost',  'Black Umbrella with Wooden Handle', 'Other', 'Admin Block',      'Left my black umbrella with a curved wooden handle near the admin block reception. Has a small sun sticker on the handle.', 'Faiz A.',    'faiz.a@college.edu',  ts(days_ago=3)),
    ('found', 'Green Decathlon Water Bottle', 'Other',       'Sports Complex',  'Green Decathlon sports bottle found near the basketball court. Has some stickers on it. Claiming? Describe the stickers!', 'Priya M.',   '9123456789',          ts(hours_ago=5)),
]

for s in samples:
    con.execute("INSERT INTO item (type,title,category,location,description,contact_name,contact_info,date_reported,status,edit_token) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (*s, 'open', str(uuid.uuid4())))
con.commit()
con.close()
print(f"✅ Seeded {len(samples)} sample items into {DB}")
