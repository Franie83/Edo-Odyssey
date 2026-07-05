#!/usr/bin/env python
"""
Script to seed restaurant owner user
Run: python scripts/seed_restaurant_owner.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.models import User

def seed_restaurant_owner():
    app = create_app()
    with app.app_context():
        # Check if restaurant owner exists
        existing = User.query.filter_by(email="restaurant@mamaebo.com").first()
        if existing:
            print(f"✅ Restaurant owner already exists: {existing.full_name}")
            return
        
        # Create restaurant owner
        user = User(
            email="restaurant@mamaebo.com",
            first_name="Adaobi",
            last_name="Nwosu",
            role="Restaurant",
            phone="+234-803-000-0000",
            is_verified=True,
            status="active",
        )
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        
        print("✅ Restaurant owner created:")
        print(f"   Email: restaurant@mamaebo.com")
        print(f"   Password: password123")
        print(f"   Name: Adaobi Nwosu")
        print(f"   Role: Restaurant")

if __name__ == "__main__":
    seed_restaurant_owner()