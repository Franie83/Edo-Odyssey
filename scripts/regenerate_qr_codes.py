#!/usr/bin/env python
"""
Script to regenerate QR codes for all attractions
Run: python scripts/regenerate_qr_codes.py
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.models import Attraction
from app.admin.routes import _generate_qr

def regenerate_all_qr_codes():
    app = create_app()
    with app.app_context():
        attractions = Attraction.query.filter_by(active=True).all()
        success_count = 0
        
        print(f"Found {len(attractions)} active attractions")
        print("=" * 50)
        
        for attraction in attractions:
            try:
                result = _generate_qr(attraction)
                if result:
                    success_count += 1
                    print(f"✅ QR code generated for: {attraction.name}")
                else:
                    print(f"❌ Failed to generate QR code for: {attraction.name}")
            except Exception as e:
                print(f"❌ Error generating QR for {attraction.name}: {str(e)}")
        
        print("=" * 50)
        print(f"Successfully generated {success_count} QR codes out of {len(attractions)} attractions")
        
        # Check if QR codes exist
        from app.models.models import QRCode
        qr_count = QRCode.query.count()
        print(f"Total QR code records in database: {qr_count}")

if __name__ == "__main__":
    regenerate_all_qr_codes()