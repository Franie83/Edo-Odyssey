import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.models import *
from datetime import datetime

app = create_app()

def import_data():
    with app.app_context():
        # Load exported data
        try:
            with open('data_export.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("❌ data_export.json not found! Run export_db.py first.")
            return
        
        print("🔄 Importing data to PostgreSQL...")
        print(f"📊 Tables to import: {', '.join(data.keys())}")
        print("=" * 50)
        
        # Import Users first
        if 'users' in data and data['users']:
            for item in data['users']:
                existing = User.query.filter_by(email=item['email']).first()
                if not existing:
                    # Remove fields that shouldn't be set manually
                    item.pop('id', None)
                    item.pop('uuid', None)
                    item.pop('created_at', None)
                    item.pop('updated_at', None)
                    item.pop('deleted_at', None)
                    
                    # Ensure password is hashed - if not, set default
                    if not item.get('password_hash'):
                        user = User(
                            email=item.get('email'),
                            first_name=item.get('first_name', 'User'),
                            last_name=item.get('last_name', ''),
                            role=item.get('role', 'Tourist'),
                            phone=item.get('phone', ''),
                            is_verified=item.get('is_verified', False),
                            heritage_points=item.get('heritage_points', 0),
                            bio=item.get('bio', ''),
                            address=item.get('address', ''),
                            nationality=item.get('nationality', ''),
                            status=item.get('status', 'active')
                        )
                        user.set_password('password123')  # Default password
                        db.session.add(user)
                    else:
                        new_user = User(**item)
                        db.session.add(new_user)
                    print(f"  ✅ Imported user: {item['email']}")
                else:
                    print(f"  ⏭️ User {item['email']} already exists")
            
            db.session.commit()
            print(f"  ✅ Users imported successfully!")
        
        # Import Categories
        if 'categories' in data and data['categories']:
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
                    print(f"  ✅ Imported category: {item['name']}")
                else:
                    print(f"  ⏭️ Category {item['name']} already exists")
            
            db.session.commit()
            print(f"  ✅ Categories imported successfully!")
        
        # Import Attractions
        if 'attractions' in data and data['attractions']:
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
                    print(f"  ✅ Imported attraction: {item['name']}")
                else:
                    print(f"  ⏭️ Attraction {item['name']} already exists")
            
            db.session.commit()
            print(f"  ✅ Attractions imported successfully!")
        
        # Import Guides
        if 'guides' in data and data['guides']:
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
                    print(f"  ✅ Imported guide (user_id: {item.get('user_id')})")
                else:
                    print(f"  ⏭️ Guide already exists")
            
            db.session.commit()
            print(f"  ✅ Guides imported successfully!")
        
        # Import Hotels
        if 'hotels' in data and data['hotels']:
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
                    print(f"  ✅ Imported hotel: {item['name']}")
                else:
                    print(f"  ⏭️ Hotel {item['name']} already exists")
            
            db.session.commit()
            print(f"  ✅ Hotels imported successfully!")
        
        # Import Restaurants
        if 'restaurants' in data and data['restaurants']:
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
                    print(f"  ✅ Imported restaurant: {item['name']}")
                else:
                    print(f"  ⏭️ Restaurant {item['name']} already exists")
            
            db.session.commit()
            print(f"  ✅ Restaurants imported successfully!")
        
        # Import Events
        if 'events' in data and data['events']:
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
                    print(f"  ✅ Imported event: {item['name']}")
                else:
                    print(f"  ⏭️ Event {item['name']} already exists")
            
            db.session.commit()
            print(f"  ✅ Events imported successfully!")
        
        # Import Bookings
        if 'bookings' in data and data['bookings']:
            for item in data['bookings']:
                item.pop('id', None)
                item.pop('uuid', None)
                item.pop('created_at', None)
                item.pop('updated_at', None)
                item.pop('deleted_at', None)
                new_booking = Booking(**item)
                db.session.add(new_booking)
                print(f"  ✅ Imported booking: {item.get('reference_code', '')}")
            
            db.session.commit()
            print(f"  ✅ Bookings imported successfully!")
        
        print("=" * 50)
        print("✅ All data imported successfully!")

if __name__ == "__main__":
    import_data()