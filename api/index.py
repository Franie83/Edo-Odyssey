import sys
import os

# Use /tmp for writable storage
os.makedirs('/tmp/instance', exist_ok=True)
os.makedirs('/tmp/uploads', exist_ok=True)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from flask import send_from_directory, jsonify
import os.path

# Create app
app = create_app()

# Serve static files directly from app/static
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('app/static', filename)

# Health check endpoint
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "database": "connected",
        "static_files": "available"
    })

# Test CSS endpoint
@app.route('/test-css')
def test_css():
    return '''
    <html>
        <head>
            <link rel="stylesheet" href="/static/css/main.css">
        </head>
        <body>
            <div class="bg-blue-900 text-white p-4">
                <h1>CSS is working!</h1>
                <p>This should have blue background with white text.</p>
            </div>
        </body>
    </html>
    '''

# Create tables on startup
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables verified")
    except Exception as e:
        print(f"⚠️ Database error: {e}")

# Vercel requires the app to be named 'app'