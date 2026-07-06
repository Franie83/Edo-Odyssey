import sys
import os
import json
from datetime import datetime
from sqlalchemy import text  # ADD THIS IMPORT

# Force production mode
os.environ['FLASK_ENV'] = 'production'

# Debug: Print database URL
print(f"DATABASE_URL from env: {os.environ.get('DATABASE_URL', 'NOT SET')}")

os.makedirs('/tmp/instance', exist_ok=True)
os.makedirs('/tmp/uploads', exist_ok=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from flask import send_from_directory, jsonify
from app.models.models import *

# Create app with production config
app = create_app('production')

# Debug: Print the database URI being used
print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")

# Helper function to parse dates
def parse_date(date_str):
    if not date_str:
        return None
    try:
        if isinstance(date_str, str):
            # Handle various date formats
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return date_str
    except:
        try:
            return datetime.strptime(str(date_str), '%Y-%m-%d %H:%M:%S')
        except:
            return None

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('app/static', filename)

# Health check - FIXED with text()
@app.route('/health')
def health():
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "static_files": "available"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

# Migration endpoint
@app.route('/migrate')
def migrate():
    try:
        with app.app_context():
            db.create_all()
            
            # Create admin user
            if not User.query.filter_by(email="admin@edo.gov.ng").first():
                admin = User(
                    email="admin@edo.gov.ng",
                    first_name="Admin",
                    last_name="User",
                    role="Super Admin",
                    is_verified=True,
                    status="active"
                )
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.commit()
            
            # Create categories
            categories = [
                {"name": "History & Museum", "type": "attraction", "icon": "bi-building-fill", "color": "#1a3a6b"},
                {"name": "UNESCO Heritage", "type": "attraction", "icon": "bi-globe", "color": "#c9a227"},
                {"name": "Nature & Wildlife", "type": "attraction", "icon": "bi-tree-fill", "color": "#2d8a4e"},
                {"name": "Adventure & Hiking", "type": "attraction", "icon": "bi-signpost-fill", "color": "#e05c27"},
            ]
            for cat_data in categories:
                if not Category.query.filter_by(name=cat_data["name"]).first():
                    cat = Category(**cat_data)
                    db.session.add(cat)
            db.session.commit()
            
        return jsonify({
            "status": "success",
            "message": "Database initialized successfully!",
            "admin_login": {
                "email": "admin@edo.gov.ng",
                "password": "admin123"
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Import data endpoint
@app.route('/import-data')
def import_data():
    try:
        # Check if data file exists
        data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data_export.json')
        
        if not os.path.exists(data_file):
            return jsonify({
                "success": False,
                "error": "data_export.json not found. Please run export_db.py first.",
                "path": data_file
            }), 404
        
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        imported_count = 0
        skipped_count = 0
        
        with app.app_context():
            # Import Users
            if 'users' in data:
                for item in data['users']:
                    existing = User.query.filter_by(email=item['email']).first()
                    if not existing:
                        # Parse date fields
                        if 'last_login' in item:
                            item['last_login'] = parse_date(item['last_login'])
                        if 'deleted_at' in item:
                            item['deleted_at'] = parse_date(item['deleted_at'])
                        
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        new_user = User(**item)
                        db.session.add(new_user)
                        imported_count += 1
                    else:
                        skipped_count += 1
                db.session.commit()
            
            # Import Categories
            if 'categories' in data:
                for item in data['categories']:
                    existing = Category.query.filter_by(name=item['name']).first()
                    if not existing:
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_cat = Category(**item)
                        db.session.add(new_cat)
                        imported_count += 1
                    else:
                        skipped_count += 1
                db.session.commit()
            
            # Import Attractions
            if 'attractions' in data:
                for item in data['attractions']:
                    existing = Attraction.query.filter_by(name=item['name']).first()
                    if not existing:
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_attraction = Attraction(**item)
                        db.session.add(new_attraction)
                        imported_count += 1
                    else:
                        skipped_count += 1
                db.session.commit()
            
            # Import Guides
            if 'guides' in data:
                for item in data['guides']:
                    existing = Guide.query.filter_by(user_id=item.get('user_id')).first()
                    if not existing:
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_guide = Guide(**item)
                        db.session.add(new_guide)
                        imported_count += 1
                    else:
                        skipped_count += 1
                db.session.commit()
            
            # Import Hotels
            if 'hotels' in data:
                for item in data['hotels']:
                    existing = Hotel.query.filter_by(name=item['name']).first()
                    if not existing:
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_hotel = Hotel(**item)
                        db.session.add(new_hotel)
                        imported_count += 1
                    else:
                        skipped_count += 1
                db.session.commit()
            
            # Import Restaurants
            if 'restaurants' in data:
                for item in data['restaurants']:
                    existing = Restaurant.query.filter_by(name=item['name']).first()
                    if not existing:
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_restaurant = Restaurant(**item)
                        db.session.add(new_restaurant)
                        imported_count += 1
                    else:
                        skipped_count += 1
                db.session.commit()
            
            # Import Events
            if 'events' in data:
                for item in data['events']:
                    existing = Event.query.filter_by(name=item['name']).first()
                    if not existing:
                        if 'date' in item:
                            item['date'] = parse_date(item['date'])
                        if 'end_date' in item:
                            item['end_date'] = parse_date(item['end_date'])
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_event = Event(**item)
                        db.session.add(new_event)
                        imported_count += 1
                    else:
                        skipped_count += 1
                db.session.commit()
            
            # Import Bookings
            if 'bookings' in data:
                for item in data['bookings']:
                    existing = Booking.query.filter_by(reference_code=item.get('reference_code')).first()
                    if not existing:
                        if 'start_date' in item:
                            item['start_date'] = parse_date(item['start_date'])
                        if 'end_date' in item:
                            item['end_date'] = parse_date(item['end_date'])
                        if 'approved_at' in item:
                            item['approved_at'] = parse_date(item['approved_at'])
                        if 'confirmed_at' in item:
                            item['confirmed_at'] = parse_date(item['confirmed_at'])
                        if 'completed_at' in item:
                            item['completed_at'] = parse_date(item['completed_at'])
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_booking = Booking(**item)
                        db.session.add(new_booking)
                        imported_count += 1
                    else:
                        skipped_count += 1
                db.session.commit()
            
            # Import Reviews
            if 'reviews' in data:
                for item in data['reviews']:
                    item.pop('id', None)
                    item.pop('uuid', None)
                    item.pop('created_at', None)
                    item.pop('updated_at', None)
                    item.pop('deleted_at', None)
                    new_review = Review(**item)
                    db.session.add(new_review)
                    imported_count += 1
                db.session.commit()
            
            # Import QR Codes
            if 'qr_codes' in data:
                for item in data['qr_codes']:
                    item.pop('id', None)
                    item.pop('created_at', None)
                    item.pop('updated_at', None)
                    new_qr = QRCode(**item)
                    db.session.add(new_qr)
                    imported_count += 1
                db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Successfully imported {imported_count} records!",
            "imported": imported_count,
            "skipped": skipped_count,
            "tables": list(data.keys())
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Create tables on startup
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables verified")
        
        # Create admin user if not exists
        if not User.query.filter_by(email="admin@edo.gov.ng").first():
            admin = User(
                email="admin@edo.gov.ng",
                first_name="Admin",
                last_name="User",
                role="Super Admin",
                is_verified=True,
                status="active"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created on startup")
    except Exception as e:
        print(f"⚠️ Database error: {e}")

# Vercel requires the app to be named 'app'