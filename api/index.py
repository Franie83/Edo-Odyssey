import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from flask import jsonify

app = create_app()

# Try to create tables on startup
try:
    with app.app_context():
        db.create_all()
        print("✅ Database tables verified")
except Exception as e:
    print(f"⚠️ Database connection issue: {e}")

@app.route('/')
def home():
    return jsonify({
        "message": "Edo Odyssey API is running!",
        "status": "connected",
        "database": "PostgreSQL"
    })

@app.route('/health')
def health():
    try:
        with app.app_context():
            db.engine.execute("SELECT 1")
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/migrate')
def migrate():
    try:
        from .migrate import run_migration
        result = run_migration()
        return jsonify({"status": "success", "message": "Database migrated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500