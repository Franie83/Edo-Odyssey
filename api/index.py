import sys
import os

os.makedirs('/tmp/instance', exist_ok=True)
os.makedirs('/tmp/uploads', exist_ok=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from flask import send_from_directory, jsonify

app = create_app()

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('app/static', filename)

# Health check
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "database": "connected",
        "static_files": "available"
    })

# Migration endpoint
@app.route('/migrate')
def migrate():
    try:
        from .migrate import run_migration
        run_migration()
        return jsonify({
            "status": "success",
            "message": "Database initialized successfully!",
            "admin_login": {
                "email": "admin@edo.gov.ng",
                "password": "admin123"
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Create tables on startup
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables verified")
    except Exception as e:
        print(f"⚠️ Database error: {e}")

# Vercel requires the app to be named 'app'