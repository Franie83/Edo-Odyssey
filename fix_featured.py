from app import create_app
from app.extensions import db
from app.models.models import Attraction, Hotel, Event

app = create_app()
with app.app_context():
    print("🔧 Fixing featured items...")
    
    # Fix Attractions - mark ALL as active and first 3 as featured
    attractions = Attraction.query.all()
    for i, att in enumerate(attractions):
        att.active = True
        att.status = "active"
        if i < 3:  # Mark first 3 as featured
            att.featured = True
        else:
            att.featured = False
        print(f"  - {att.name}: featured={att.featured}, active={att.active}")
    
    # Fix Hotels - mark first 2 as featured
    hotels = Hotel.query.all()
    for i, hotel in enumerate(hotels):
        if i < 2:  # Mark first 2 as featured
            hotel.featured = True
        print(f"  - {hotel.name}: featured={hotel.featured}")
    
    # Fix Events - mark first 2 as featured
    events = Event.query.all()
    for i, event in enumerate(events):
        event.active = True
        event.status = "active"
        if i < 2:  # Mark first 2 as featured
            event.featured = True
        print(f"  - {event.name}: featured={event.featured}")
    
    db.session.commit()
    
    print("\n✅ Summary:")
    print(f"  - Featured Attractions: {Attraction.query.filter_by(featured=True).count()}")
    print(f"  - Featured Hotels: {Hotel.query.filter_by(featured=True).count()}")
    print(f"  - Featured Events: {Event.query.filter_by(featured=True).count()}")
    
    # Show which attractions are featured
    print("\n📋 Featured Attractions:")
    for att in Attraction.query.filter_by(featured=True).all():
        print(f"  - {att.name}")