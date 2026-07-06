import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    print("🔄 Creating database tables...")
    db.create_all()
    print("✅ Tables created successfully!")
    
    # Create admin user
    from app.models.models import User
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
        db.session.commit()
        print("✅ Admin user created: admin@edo.gov.ng / admin123")
    else:
        print("✅ Admin user already exists")