import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.models import Attraction

def update_images():
    app = create_app()
    with app.app_context():
        image_map = {
            "The Royal Court of Benin (Oba's Palace)": "https://images.unsplash.com/photo-1580654712603-eb43273aff33?auto=format&fit=crop&q=80&w=800",
            "Igun Street Bronzecasting Guild": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=800",
            "Okomu National Park": "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&q=80&w=800",
            "Ancient Benin Moats (Iya)": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&q=80&w=800",
            "Osun Sacred Grove (Iguae-Okun)": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&q=80&w=800",
            "Eki Market (Ring Road)": "https://images.unsplash.com/photo-1565031491910-e57fac031c41?auto=format&fit=crop&q=80&w=800"
        }
        
        print("🔄 Updating attraction images...")
        for name, url in image_map.items():
            att = Attraction.query.filter_by(name=name).first()
            if att:
                att.image_url = url
                print(f"✅ Updated: {name}")
            else:
                print(f"❌ Not found: {name}")
        
        db.session.commit()
        print("\n✅ All images updated successfully!")

if __name__ == "__main__":
    update_images()