from app import create_app
from app.extensions import db
from app.models.models import Attraction

app = create_app()
with app.app_context():
    # Get all attractions
    attractions = Attraction.query.all()
    
    print("📋 Current attractions:")
    for att in attractions:
        print(f"  - {att.name}: featured={att.featured}")
    
    # Mark first 3 as featured
    print("\n⭐ Marking first 3 as featured...")
    for i, att in enumerate(attractions[:3]):
        att.featured = True
        att.active = True
        att.status = "active"
        print(f"  ✅ {att.name} is now featured!")
    
    db.session.commit()
    
    print("\n✅ Updated attractions:")
    for att in Attraction.query.filter_by(featured=True).all():
        print(f"  - {att.name}")