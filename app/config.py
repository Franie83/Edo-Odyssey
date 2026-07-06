import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    
    # Database configuration - SQLite by default
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Use SQLite if no DATABASE_URL is provided
    if DATABASE_URL:
        # Fix for Railway's postgres:// vs postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Default to SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///edo_odyssey.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
    }
    
    # Upload configuration - Use /tmp for cloud platforms, local for development
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('VERCEL_ENV'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Base URL - Detect environment
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        BASE_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'https://edo-odyssey.up.railway.app')
    elif os.environ.get('VERCEL_ENV'):
        BASE_URL = os.environ.get('BASE_URL', 'https://edo-odyssey.vercel.app')
    else:
        BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    
    # Cloudinary configuration for image uploads
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    WTF_CSRF_ENABLED = False
    
    # SSL settings
    PREFERRED_URL_SCHEME = 'https'
    FORCE_SSL = True

class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///edo_odyssey.db'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    FORCE_SSL = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True
    
    # Use SQLite in production if no DATABASE_URL
    if not os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///edo_odyssey.db'
    
    # Auto-detect production URL
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        BASE_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'https://edo-odyssey.up.railway.app')
    elif os.environ.get('VERCEL_ENV'):
        BASE_URL = os.environ.get('BASE_URL', 'https://edo-odyssey.vercel.app')
    else:
        BASE_URL = os.environ.get('BASE_URL', 'https://edo-odyssey.vercel.app')

class RailwayConfig(ProductionConfig):
    """Special config for Railway deployment"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True
    
    # Railway specific
    BASE_URL = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'https://edo-odyssey.up.railway.app')
    PREFERRED_URL_SCHEME = 'https'
    
    # Use PostgreSQL if available, otherwise SQLite
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            return db_url
        return 'sqlite:///edo_odyssey.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'railway': RailwayConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the appropriate config based on environment"""
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        return RailwayConfig
    elif os.environ.get('VERCEL_ENV'):
        return ProductionConfig
    elif os.environ.get('FLASK_ENV') == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig