# 🔍 FindIt — College Lost & Found Portal

A lightweight Flask web app to help your college community reunite lost belongings with their owners.

---

## ✨ Features

- **Post Lost / Found items** — with image upload, category, location, and contact info
- **Browse & Search** — filter by type, category, location, and status
- **Token-based ownership** — no login needed; a secret link lets you resolve your own post
- **Pastel UI** — clean, friendly design with Fraunces + DM Sans typography

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

The app starts at **http://127.0.0.1:5000**

The SQLite database (`lostandfound.db`) and `static/uploads/` folder are created automatically on first run.

### 3. (Optional) Seed demo data
```bash
python seed.py
```
This adds 8 sample items so the home page isn't empty on first load.

---

## 📁 Project Structure

```
lost-and-found/
├── app.py                  # Flask app — routes, models, config
├── seed.py                 # Demo data seeder
├── requirements.txt
├── templates/
│   ├── base.html           # Shared layout, nav, styles
│   ├── index.html          # Home page
│   ├── items.html          # Browse + search page
│   ├── item_detail.html    # Single item detail page
│   └── post.html           # Post new item form
└── static/
    └── uploads/            # Uploaded item images (auto-created)
```

---

## 🔐 How Resolving Works (No Login)

When a user posts an item, the app generates a UUID `edit_token` stored in the DB.
The detail page URL includes `?token=<uuid>`. Only visitors with that token see the
**"Mark as Resolved"** button. Users are prompted to bookmark this link after posting.

---

## 🛠 Tech Stack

| Layer     | Technology                    |
|-----------|-------------------------------|
| Backend   | Python 3.10+ / Flask 3.0      |
| Database  | SQLite via Flask-SQLAlchemy   |
| Images    | Pillow (resize to 800×800)    |
| Frontend  | Jinja2 + Vanilla CSS/JS       |
| Fonts     | Google Fonts (Fraunces + DM Sans) |

---

## 🌱 Future Ideas

- Email notification when someone contacts about your item
- Admin panel to moderate listings
- College email login (restrict to `@college.edu`)
- Expiry: auto-archive posts older than 30 days
- WhatsApp contact button
