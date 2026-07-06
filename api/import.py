import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import jsonify
from app import create_app
from app.extensions import db
from app.models.models import *

app = create_app()

def run_import():
    with app.app_context():
        try:
            # Load data
            with open('data_export.json', 'r') as f:
                data = json.load(f)
            
            imported_count = 0
            errors = []
            
            # Import Users
            if 'users' in data:
                for item in data['users']:
                    existing = User.query.filter_by(email=item['email']).first()
                    if not existing:
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_user = User(**item)
                        db.session.add(new_user)
                        imported_count += 1
            
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
            
            db.session.commit()
            
            # Import Guides
            if 'guides' in data:
                for item in data['guides']:
                    item.pop('id', None)
                    item.pop('uuid', None)
                    item.pop('created_at', None)
                    item.pop('updated_at', None)
                    item.pop('deleted_at', None)
                    existing = Guide.query.filter_by(user_id=item.get('user_id')).first()
                    if not existing:
                        new_guide = Guide(**item)
                        db.session.add(new_guide)
                        imported_count += 1
            
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
            
            db.session.commit()
            
            # Import Events
            if 'events' in data:
                for item in data['events']:
                    existing = Event.query.filter_by(name=item['name']).first()
                    if not existing:
                        item.pop('id', None)
                        item.pop('uuid', None)
                        item.pop('created_at', None)
                        item.pop('updated_at', None)
                        item.pop('deleted_at', None)
                        new_event = Event(**item)
                        db.session.add(new_event)
                        imported_count += 1
            
            db.session.commit()
            
            # Import Bookings
            if 'bookings' in data:
                for item in data['bookings']:
                    item.pop('id', None)
                    item.pop('uuid', None)
                    item.pop('created_at', None)
                    item.pop('updated_at', None)
                    item.pop('deleted_at', None)
                    new_booking = Booking(**item)
                    db.session.add(new_booking)
                    imported_count += 1
            
            db.session.commit()
            
            return {
                "success": True,
                "message": f"Successfully imported {imported_count} records!",
                "tables": list(data.keys())
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

if __name__ == "__main__":
    result = run_import()
    print(result)