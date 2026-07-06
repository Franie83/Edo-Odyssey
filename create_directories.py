import os

def create_directories():
    """Create all necessary directories for the application"""
    directories = [
        'instance',  # SQLite database location
        'app/static/uploads',
        'app/static/uploads/attractions',
        'app/static/uploads/qr_codes',
        'app/static/uploads/hotels',
        'app/static/uploads/restaurants',
        'app/static/uploads/events',
        'app/static/uploads/guides',
        'app/static/uploads/news',
        'app/static/uploads/users',
        'app/static/images',
        '/tmp/uploads',
        '/tmp/uploads/attractions',
        '/tmp/uploads/qr_codes',
        '/tmp/instance',
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
        except Exception as e:
            print(f"⚠️ Could not create {directory}: {e}")

if __name__ == "__main__":
    print("🔄 Creating directories...")
    create_directories()
    print("\n✅ All directories created successfully!")