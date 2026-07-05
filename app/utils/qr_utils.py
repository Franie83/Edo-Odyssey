import os
import qrcode
from flask import current_app, url_for
from app.models.models import QRCode, Attraction
from app.extensions import db

def generate_qr_code(attraction_id):
    """Generate QR code for an attraction and save to database and file system"""
    try:
        from PIL import Image
        
        # Get the attraction
        attraction = Attraction.query.get(attraction_id)
        if not attraction:
            return None
        
        # Create directory if it doesn't exist
        qr_dir = os.path.join(current_app.root_path, 'static/uploads/qr_codes')
        os.makedirs(qr_dir, exist_ok=True)
        
        # Generate QR code data (URL to attraction detail page)
        qr_data = url_for('attractions.detail', id=attraction_id, _external=True)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image
        filename = f"qr_{attraction_id}.png"
        filepath = os.path.join(qr_dir, filename)
        img.save(filepath, 'PNG')
        
        # Update or create QR code record in database
        qr_code = QRCode.query.filter_by(attraction_id=attraction_id).first()
        if qr_code:
            qr_code.code = filename
            qr_code.url = qr_data
        else:
            qr_code = QRCode(
                attraction_id=attraction_id,
                code=filename,
                url=qr_data
            )
            db.session.add(qr_code)
        
        db.session.commit()
        return filename
        
    except ImportError:
        print("QRCode library not installed. Install with: pip install qrcode Pillow")
        return None
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return None

def regenerate_all_qr_codes():
    """Regenerate QR codes for all attractions"""
    attractions = Attraction.query.filter_by(active=True).all()
    success_count = 0
    for attraction in attractions:
        result = generate_qr_code(attraction.id)
        if result:
            success_count += 1
            print(f"Generated QR code for attraction {attraction.id}: {attraction.name}")
    print(f"Generated {success_count} QR codes out of {len(attractions)} attractions")
    return success_count