import os
from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    
    # Database configuration - Vercel PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///edo_odyssey.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Upload configuration - Vercel uses /tmp
    UPLOAD_FOLDER = '/tmp/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Base URL for QR codes
    BASE_URL = os.environ.get('BASE_URL', 'https://edo-odyssey.vercel.app')
    
    # Session configuration
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CSRF Protection
    WTF_CSRF_ENABLED = False
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@edo-odyssey.com')

class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    BASE_URL = os.environ.get('BASE_URL', 'https://edo-odyssey.vercel.app')
    WTF_CSRF_ENABLED = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}