# 🧭 Edo Odyssey — Official Edo State Tourism Platform

> A world-class, production-ready digital tourism platform built for the **Edo State Tourism Agency (ESTA)**, Nigeria.

---

## 🗺 Overview

**Edo Odyssey** is a full-featured web application that allows tourists, guides, hotels, and restaurants to connect through a single, government-backed platform. Built on **Python Flask**, it covers the full lifecycle of tourism in Edo State — from discovering attractions to booking guides, leaving reviews, and reading news.

---

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Python 3.10+ installed
- `pip` available

### Installation

```bash
# 1. Enter the project directory
cd edo_odyssey

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python run.py
```

The app will launch at **http://localhost:5000** and automatically:
- Create the SQLite database
- Seed all demo data (attractions, guides, hotels, events, news, users)
- Print all quick-login credentials in the terminal

---

## 🔑 Quick Demo Logins

Use these credentials to immediately explore every role — or click the **Quick Demo Login** buttons on the home page or login page.

| Role | Email | Password | What You Can Do |
|------|-------|----------|-----------------|
| **Super Admin** | superadmin@edo.gov.ng | superadmin123 | Full platform control, ZIP download, user management |
| **Agency Admin** | admin@edo.gov.ng | admin123 | Manage content, approve guides, export data |
| **Tourist** | tourist@gmail.com | tourist123 | Browse, book, review, favourite |
| **Tourist 2** | jane@visitor.com | tourist123 | Alternate tourist account |
| **Guide** | guide@edo.gov.ng | guide123 | View guide profile and bookings |
| **Hotel Manager** | hotel@emotan.com | hotel123 | Hotel-owner perspective |
| **Restaurant Owner** | restaurant@mamaebo.com | mamaebo123 | Restaurant perspective |

---

## 🌟 Feature Walkthrough

### 🏛 Public Visitors
1. **Home Page** — Hero banner, quick-login bar, featured attractions, guides, events, hotels, and news
2. **Explore Attractions** — Filter by category, sort by price/views, search by name; each has QR code, map, reviews
3. **Tour Guides** — Browse ESTA-certified guides; filter by language; view profiles with ratings
4. **Hotels** — Filter by stars and price; view rooms, facilities, and reviews
5. **Restaurants** — Browse by cuisine; view menus and reviews
6. **Events** — Upcoming / past filter; live countdown timers; ticket booking
7. **News** — Featured articles, commenting system, share buttons
8. **Global Search** — Type anything; results across all entity types instantly

### 👤 Registered Tourists
1. **Register** — Choose Tourist / Guide / Hotel / Restaurant role
2. **Dashboard** — See all bookings with status, reviews given, notifications, quick actions
3. **Book Services** — Hotels, guides, tours, events with automatic price calculation
4. **Cancel Bookings** — Self-service cancellation for pending bookings
5. **Leave Reviews** — Rate and comment on any attraction, hotel, guide, or restaurant
6. **Favourites** — Heart-icon any attraction to save it
7. **Heritage Points** — Earned by exploring the platform
8. **Profile** — Edit name, phone, nationality, bio, and change password

### 🛡 Admin Panel (`/admin`)
Access via **Super Admin** or **Agency Admin** quick-login.

| Section | What It Does |
|---------|-------------|
| **Dashboard** | Stats overview, booking trend chart, recent bookings, broadcast notifications, audit log preview |
| **Attractions** | Full CRUD — create, edit, delete; toggle featured; regenerate QR codes |
| **Guides** | List all guides, verify/approve/reject with dropdown; edit profile |
| **Hotels** | Full CRUD with facilities, stars, price, and room types |
| **Restaurants** | Full CRUD with cuisine, menu items, price range |
| **Events** | Full CRUD with countdown timers, location, capacity |
| **News** | Write and publish articles; toggle featured |
| **Users** | View all users, edit roles, toggle verification, create new users |
| **Bookings** | View all bookings, change status (Pending → Confirmed → Completed → Cancelled) |
| **Reviews** | Approve or delete any review |
| **Categories** | Create attraction categories with icon and colour |
| **Analytics** | Monthly booking trend, revenue chart, booking-by-type donut, user role pie, top attractions |
| **CMS Settings** | Edit hero text, contact details, about content, policy pages |
| **FAQs** | Add and delete FAQ items by category |
| **Partners** | Add/remove partner logos and sponsor links |
| **Audit Logs** | Every admin action is logged with timestamp, user, role, and IP |
| **Download ZIP** | One-click download of the entire project source code |

### 📱 API Layer (`/api`)
| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check — uptime, db status |
| `GET /api/attractions` | JSON list of all attractions |
| `GET /api/guides` | JSON list of approved guides |
| `GET /api/hotels` | JSON list of hotels |
| `GET /api/events` | JSON list of upcoming events |
| `GET /api/search?q=...` | Global search across all entity types |
| `GET /api/stats` | Platform summary statistics |

### 📸 QR Codes
- Every attraction gets an auto-generated QR code on creation
- QR codes link to `/qr/scan/<attraction_id>` which increments the scan counter and redirects to the attraction page
- Admins can regenerate QR codes from the admin panel

---

## 🏗 Project Architecture

```
edo_odyssey/
├── run.py                    # Entry point — seeds DB and starts server
├── config.py                 # Dev (SQLite) and Production (PostgreSQL) configs
├── requirements.txt          # All Python dependencies
└── app/
    ├── __init__.py           # App factory — registers all 15 blueprints
    ├── extensions.py         # db, login_manager, migrate, csrf
    ├── models/
    │   └── models.py         # 20+ SQLAlchemy models with soft delete
    ├── utils/
    │   ├── helpers.py        # inject_globals, file upload, audit log, notify
    │   ├── decorators.py     # @admin_required, @super_admin_required, @role_required
    │   └── seed.py           # Full demo data seeder
    ├── auth/routes.py        # Login, register, logout, quick_login
    ├── main/routes.py        # Home, about, contact, privacy, terms, faq
    ├── attractions/routes.py # List (filter/sort/search), detail (views, QR, nearby)
    ├── guides/routes.py      # List (filter by language), detail with reviews
    ├── hotels/routes.py      # List, detail with rooms and reviews
    ├── restaurants/routes.py # List, detail with menus and reviews
    ├── events/routes.py      # List (upcoming/past), detail with countdown
    ├── news/routes.py        # List, detail, comments
    ├── bookings/routes.py    # New booking, cancel
    ├── reviews/routes.py     # Add/update review for any entity
    ├── dashboard/routes.py   # User dashboard, profile, notifications, favourites
    ├── search/routes.py      # Global search
    ├── qr/routes.py          # QR scan redirect and counter
    ├── admin/routes.py       # Full admin CRUD, analytics, export, ZIP
    └── api/routes.py         # JSON API endpoints
```

---

## 🗄 Key Models

| Model | Purpose |
|-------|---------|
| `User` | Auth, roles (Tourist/Guide/Hotel/Restaurant/Admin/Super Admin), heritage points |
| `Attraction` | Heritage sites with category, QR, views, ticket price |
| `Guide` | Tour guide profile with verification, languages, rates |
| `Hotel` | Accommodation with rooms, stars, facilities |
| `Restaurant` | Dining with menus, cuisine, price range |
| `Event` | Festivals and events with countdown, capacity |
| `News` | Articles with comments, featured flag, tags |
| `Booking` | Hotel/Guide/Tour/Event bookings with auto-pricing |
| `Review` | Star rating + comment for any entity type |
| `QRCode` | Auto-generated QR per attraction, scan counter |
| `AuditLog` | Admin action log — user, role, action, IP, timestamp |
| `CMSSetting` | Key-value store for all CMS content |
| `Notification` | User notifications, read/unread |
| `FAQ` | Public FAQ items by category |
| `Partner` | Sponsor/partner logos and links |
| `Favourite` | User → entity polymorphic favourites |

All models extend `BaseModel` which provides: `id` (UUID), `created_at`, `updated_at`, `created_by`, `status`, `deleted_at`, and a `soft_delete()` method.

---

## ⚙ Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `FLASK_ENV` | `development` | `development` uses SQLite; `production` uses PostgreSQL |
| `SECRET_KEY` | auto-generated | Flask session secret |
| `SESSION_SECRET` | — | Override via Replit Secrets |
| `DATABASE_URL` | *(ignored in dev)* | PostgreSQL URL for production |
| `PORT` | `5000` | Override the listening port |

---

## 🚀 Production Deployment

1. Set `FLASK_ENV=production` and `DATABASE_URL` to your PostgreSQL connection string
2. Run `flask db upgrade` to apply migrations
3. Use a production WSGI server: `gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"`

---

## 🎨 Design System

| Token | Value |
|-------|-------|
| Royal Blue | `#1a3a6b` |
| Gold | `#c9a227` |
| Font (headings) | Playfair Display |
| Font (body) | Inter |
| Framework | Bootstrap 5.3 |

---

## 📦 Dependencies

```
Flask                  Flask web framework
Flask-SQLAlchemy       ORM and database abstraction
Flask-Login            Session-based authentication
Flask-WTF / WTForms    CSRF protection and forms
Flask-Migrate          Database migration via Alembic
qrcode[pil]            QR code generation
Pillow                 Image processing
openpyxl               Excel (.xlsx) export
reportlab              PDF generation
PyJWT                  JWT tokens for API
bleach                 HTML sanitization
email-validator        Email validation
Werkzeug               Password hashing, file uploads
```

---

## 📝 License

© 2026 Edo State Tourism Agency (ESTA). All rights reserved.
Built as the official tourism digital platform for Edo State, Nigeria.
