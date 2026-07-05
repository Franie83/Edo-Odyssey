from app import create_app
from app.models.models import Attraction, Hotel, Event, Guide

app = create_app()
with app.app_context():
    # Check Attraction
    att = Attraction.query.first()
    print(f'Attraction has featured: {hasattr(att, "featured")}')
    if att and hasattr(att, "featured"):
        print(f'  - {att.name}: featured={att.featured}')
    
    # Check Hotel
    hotel = Hotel.query.first()
    print(f'Hotel has featured: {hasattr(hotel, "featured")}')
    if hotel and hasattr(hotel, "featured"):
        print(f'  - {hotel.name}: featured={hotel.featured}')
    
    # Check Event
    event = Event.query.first()
    print(f'Event has featured: {hasattr(event, "featured")}')
    if event and hasattr(event, "featured"):
        print(f'  - {event.name}: featured={event.featured}')
    
    # Check Guide
    guide = Guide.query.first()
    print(f'Guide has featured: {hasattr(guide, "featured")}')
    if guide and hasattr(guide, "featured"):
        print(f'  - {guide.user.full_name if guide.user else "Unknown"}: featured={guide.featured}')
    
    # Count featured items
    print("\n📊 Featured Counts:")
    print(f"  - Featured Attractions: {Attraction.query.filter_by(featured=True).count()}")
    print(f"  - Featured Hotels: {Hotel.query.filter_by(featured=True).count()}")
    print(f"  - Featured Events: {Event.query.filter_by(featured=True).count()}")