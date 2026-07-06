from app import create_app
from app.extensions import db
from app.models.models import User, Category, Attraction, Guide, Hotel, Restaurant, Event, Booking, Review, QRCode

app = create_app()

with app.app_context():
    print("🔄 Creating database tables...")
    
    # Create all tables
    db.create_all()
    print("✅ Tables created successfully!")
    
    # Create admin user if not exists
    if not User.query.filter_by(email="admin@edo.gov.ng").first():
        admin = User(
            email="admin@edo.gov.ng",
            first_name="Admin",
            last_name="User",
            role="Super Admin",
            is_verified=True,
            status="active"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        print("✅ Admin user created")
    
    # Create categories
    categories = [
        {"name": "History & Museum", "type": "attraction", "icon": "bi-building-fill", "color": "#1a3a6b"},
        {"name": "UNESCO Heritage", "type": "attraction", "icon": "bi-globe", "color": "#c9a227"},
        {"name": "Nature & Wildlife", "type": "attraction", "icon": "bi-tree-fill", "color": "#2d8a4e"},
        {"name": "Adventure & Hiking", "type": "attraction", "icon": "bi-signpost-fill", "color": "#e05c27"},
    ]
    for cat_data in categories:
        if not Category.query.filter_by(name=cat_data["name"]).first():
            cat = Category(**cat_data)
            db.session.add(cat)
            print(f"✅ Category created: {cat_data['name']}")
    
    db.session.commit()
    print("✅ Database initialization complete!")
    print("")
    print("📋 Login Credentials:")
    print("   Email: admin@edo.gov.ng")
    print("   Password: admin123")