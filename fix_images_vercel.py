from app import create_app
from app.extensions import db
from app.models.models import Attraction

app = create_app()

# Map of attractions to Unsplash URLs
image_map = {
    'The Royal Court of Benin (Oba\'s Palace)': 'https://images.unsplash.com/photo-1580654712603-eb43273aff33?auto=format&fit=crop&q=80&w=800',
    'Igun Street Bronzecasting Guild': 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=800',
    'Okomu National Park': 'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&q=80&w=800',
    'Ancient Benin Moats (Iya)': 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&q=80&w=800',
    'Osun Sacred Grove (Iguae-Okun)': 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&q=80&w=800',
    'Eki Market (Ring Road)': 'https://images.unsplash.com/photo-1565031491910-e57fac031c41?auto=format&fit=crop&q=80&w=800'
}

with app.app_context():
    print("🔄 Updating attraction images...")
    
    for name, url in image_map.items():
        attraction = Attraction.query.filter_by(name=name).first()
        if attraction:
            attraction.image_url = url
            print(f"  ✅ Updated: {name}")
        else:
            print(f"  ❌ Not found: {name}")
    
    db.session.commit()
    print("\n✅ All images updated successfully!")