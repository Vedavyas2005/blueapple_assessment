# 🍎 BlueApple — Slot Booking System

A clean, full-stack slot booking web app built with **Python + Flask + MySQL**. Users can browse available time slots and make reservations. Admins get a full dashboard to manage everything.

---

## ✨ Features

- 🔐 User registration & login with persistent sessions (Flask-Login)
- 🛡️ Admin role unlocked via secret passphrase at sign-up
- 📅 7-day date strip with live slot availability
- 🗓️ Click-to-book drawer with purpose & notes
- 📋 My Bookings — full history with cancel support
- ⚙️ Admin dashboard — stats, slot management, booking control, user directory
- 📦 Bulk slot creation (e.g. seed a whole week in one go)
- 🔌 JSON API endpoints (`/api/slots`, `/api/my-bookings`)
- 📱 Fully responsive

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.13, Flask 3.1 |
| Auth | Flask-Login 0.6 |
| ORM | Flask-SQLAlchemy 3.1 |
| Database | MySQL 8.x (via PyMySQL) |
| Frontend | Jinja2, HTML5, CSS3, Vanilla JS |
| Fonts | Syne + DM Sans |

---

## 📁 Folder Structure

```
blueapple/
├── .env                    # DB credentials & secrets
├── requirements.txt
├── run.py                  # Entry point
├── init_db.py              # Creates tables + seeds slots
│
├── app/
│   ├── __init__.py         # App factory
│   ├── config.py
│   ├── models.py           # User, Slot, Booking
│   ├── auth/routes.py      # /auth/login  /register  /logout
│   ├── main/routes.py      # /  /book/<id>  /my-bookings  /cancel/<id>
│   ├── admin/routes.py     # /admin/*
│   └── api/routes.py       # /api/slots  /api/my-bookings
│
├── templates/
│   ├── base.html
│   ├── auth/               # login.html, register.html
│   ├── main/               # index.html, my_bookings.html
│   └── admin/              # dashboard, slots, add_slot, bookings, users
│
└── static/
    ├── css/main.css
    └── js/main.js
```

---

## 🚀 Getting Started

### 1. Clone & set up

```bash
git clone https://github.com/yourname/blueapple.git
cd blueapple
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

### 2. Create the MySQL database

```sql
CREATE DATABASE blueapple_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Configure `.env`

```env
SECRET_KEY=your-secret-key-here
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=blueapple_db
ADMIN_SECRET=adminauth
```

### 4. Initialise DB & seed slots

```bash
python init_db.py
```

### 5. Run

```bash
python run.py
# → http://127.0.0.1:5000
```

---

## 👤 Accounts

| Role | How to create |
|---|---|
| Regular user | Register normally, leave admin secret blank |
| Admin | Enter `adminauth` in the admin secret field at registration |

---

## 🗃️ Database Schema

```
users     → id, name, email, password_hash, phone, is_admin, created_at
slots     → id, date, start_time, end_time, capacity, is_active, created_at
bookings  → id, reference, user_id, slot_id, purpose, notes, status, created_at
```

Booking references are auto-generated in the format `BA-20240319-A3F2C1`.

---

## 🔒 Security Notes

- Passwords hashed with Werkzeug (PBKDF2-SHA256) — never stored in plain text
- Sessions signed with `SECRET_KEY` — change this before deploying
- All admin routes protected by a custom `@admin_required` decorator
- Change `ADMIN_SECRET` from the default before going live

---

## 🐛 Common Issues

| Error | Fix |
|---|---|
| `Access denied for user 'root'` | Wrong `DB_PASSWORD` in `.env` |
| `Can't connect to MySQL` | MySQL service not running — start it in Windows Services |
| `No module named flask` | Run `venv\Scripts\activate` first |
| `Table doesn't exist` | Run `python init_db.py` |
| Port 5000 in use | Change `port=5000` to `port=5001` in `run.py` |

---

## 📄 License

MIT — feel free to use and modify.
