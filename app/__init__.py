import os
# Set instance path to /tmp for Vercel
os.makedirs('/tmp/instance', exist_ok=True)
os.makedirs('/tmp/uploads', exist_ok=True)

from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
import re
from .config import config
from .extensions import db, migrate, login_manager, csrf

# Optional imports - will be loaded if available
try:
    from flask_mail import Mail
    mail = Mail()
except ImportError:
    mail = None
    print("flask-mail not installed - email features disabled")

try:
    from flask_cors import CORS
    cors = CORS
except ImportError:
    cors = None
    print("flask-cors not installed - CORS features disabled")

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Create app with static folder configuration
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static')
    app.config.from_object(config[config_name])
    
    # Force instance path to /tmp for Vercel (read-only filesystem fix)
    app.instance_path = '/tmp/instance'
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    if mail is not None:
        mail.init_app(app)
    
    if cors is not None:
        cors(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from .models.models import User
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    try:
        from .main.routes import main_bp
        app.register_blueprint(main_bp)
    except ImportError as e:
        print(f"Error loading main blueprint: {e}")
    
    try:
        from .auth.routes import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError as e:
        print(f"Error loading auth blueprint: {e}")
    
    try:
        from .admin.routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
    except ImportError as e:
        print(f"Error loading admin blueprint: {e}")
    
    try:
        from .api.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError as e:
        print(f"Error loading api blueprint: {e}")
    
    try:
        from .attractions.routes import attractions_bp
        app.register_blueprint(attractions_bp)
    except ImportError as e:
        print(f"Error loading attractions blueprint: {e}")
    
    try:
        from .guides.routes import guides_bp
        app.register_blueprint(guides_bp)
    except ImportError as e:
        print(f"Error loading guides blueprint: {e}")
    
    try:
        from .hotels.routes import hotels_bp
        app.register_blueprint(hotels_bp)
    except ImportError as e:
        print(f"Error loading hotels blueprint: {e}")
    
    try:
        from .restaurants.routes import restaurants_bp
        app.register_blueprint(restaurants_bp)
    except ImportError as e:
        print(f"Error loading restaurants blueprint: {e}")
    
    try:
        from .events.routes import events_bp
        app.register_blueprint(events_bp)
    except ImportError as e:
        print(f"Error loading events blueprint: {e}")
    
    try:
        from .news.routes import news_bp
        app.register_blueprint(news_bp)
    except ImportError as e:
        print(f"Error loading news blueprint: {e}")
    
    try:
        from .bookings.routes import bookings_bp
        app.register_blueprint(bookings_bp)
    except ImportError as e:
        print(f"Error loading bookings blueprint: {e}")
    
    try:
        from .reviews.routes import reviews_bp
        app.register_blueprint(reviews_bp)
    except ImportError as e:
        print(f"Error loading reviews blueprint: {e}")
    
    try:
        from .dashboard.routes import dashboard_bp
        app.register_blueprint(dashboard_bp)
    except ImportError as e:
        print(f"Error loading dashboard blueprint: {e}")
    
    try:
        from .qr.routes import qr_bp
        app.register_blueprint(qr_bp)
    except ImportError as e:
        print(f"Error loading qr blueprint: {e}")
    
    try:
        from .search.routes import search_bp
        app.register_blueprint(search_bp)
    except ImportError as e:
        print(f"Error loading search blueprint: {e}")
    
    # Create directories
    create_directories(app)
    
    # Template filter for image URLs (handles Google Drive and missing images)
    @app.template_filter('image_src')
    def image_src_filter(url):
        """Convert various image URLs to displayable URLs"""
        from flask import current_app
        
        if not url:
            return url_for('static', filename='images/placeholder.jpg')
        
        # Handle Google Drive URLs
        if "drive.google.com/file/d/" in url:
            import re
            match = re.search(r"/d/([^/]+)", url)
            if match:
                file_id = match.group(1)
                return f"https://drive.google.com/uc?export=view&id={file_id}"
        
        # Handle Google Drive thumbnail URLs
        if "drive.google.com/thumbnail" in url:
            import re
            match = re.search(r"id=([^&]+)", url)
            if match:
                file_id = match.group(1)
                return f"https://drive.google.com/uc?export=view&id={file_id}"
        
        # Handle local upload paths
        if url and url.startswith('/static/uploads/'):
            # Check if the file exists on Vercel (using /tmp)
            file_path = url.lstrip('/')
            # Try both locations: app/static and /tmp
            possible_paths = [
                os.path.join(current_app.root_path, file_path),
                os.path.join('/tmp', file_path.replace('static/uploads/', 'uploads/'))
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return url
            
            # Check if it's a valid URL with http
            if url.startswith('http://') or url.startswith('https://'):
                return url
        
        # Check if it's a full URL
        if url and (url.startswith('http://') or url.startswith('https://')):
            return url
        
        # Fallback to placeholder
        return url_for('static', filename='images/placeholder.jpg')
    
    # Context processor for CMS settings
    @app.context_processor
    def inject_settings():
        """Inject CMS settings into all templates."""
        try:
            from .models.models import CMSSetting
            
            settings = {
                s.key: s.value
                for s in CMSSetting.query.all()
            }
            
            return {
                "settings": settings,
                "cms": settings
            }
            
        except Exception as e:
            print(f"CMS settings error: {e}")
            return {
                "settings": {},
                "cms": {}
            }
    
    # Context processor for notifications
    @app.context_processor
    def inject_notifications():
        """Inject unread notification count for all templates"""
        if current_user.is_authenticated:
            try:
                from .models.models import Notification
                unread_notifs = Notification.query.filter_by(
                    user_id=current_user.id,
                    is_read=False
                ).count()
                return {
                    "unread_notifs": unread_notifs
                }
            except Exception as e:
                print(f"Notification error: {e}")
                return {
                    "unread_notifs": 0
                }
        return {
            "unread_notifs": 0
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    return app

def create_directories(app):
    """Create necessary directories"""
    # Use /tmp for Vercel (writable)
    upload_dir = '/tmp/uploads'
    directories = [
        upload_dir,
        os.path.join(upload_dir, 'attractions'),
        os.path.join(upload_dir, 'qr_codes'),
        os.path.join(upload_dir, 'hotels'),
        os.path.join(upload_dir, 'restaurants'),
        os.path.join(upload_dir, 'events'),
        os.path.join(upload_dir, 'guides'),
        os.path.join(upload_dir, 'news'),
        os.path.join(upload_dir, 'users'),
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)