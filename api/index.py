import sys
import os

# Use /tmp for writable storage
os.makedirs('/tmp/instance', exist_ok=True)
os.makedirs('/tmp/uploads', exist_ok=True)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db

# Create app
app = create_app()

# Create tables on startup
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables verified")
    except Exception as e:
        print(f"⚠️ Database error: {e}")

# Vercel requires the app to be named 'app'