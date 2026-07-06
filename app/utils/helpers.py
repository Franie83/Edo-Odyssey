import os
import uuid
import hashlib
from datetime import datetime
from flask import current_app, url_for, request
from werkzeug.utils import secure_filename
from PIL import Image
from ..extensions import db
from ..models.models import AuditLog, Notification

# Try to import Cloudinary
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    print("Cloudinary not installed - cloudinary features disabled")

def allowed_file(filename):
    """Check if the file extension is allowed"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def init_cloudinary():
    """Initialize Cloudinary with app config"""
    if not CLOUDINARY_AVAILABLE:
        return False
    
    try:
        cloudinary.config(
            cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
            api_key=current_app.config.get('CLOUDINARY_API_KEY'),
            api_secret=current_app.config.get('CLOUDINARY_API_SECRET'),
            secure=True
        )
        return True
    except Exception as e:
        print(f"Cloudinary init error: {e}")
        return False

def upload_to_cloudinary(file, folder="attractions"):
    """Upload a file to Cloudinary and return the URL"""
    if not file or not CLOUDINARY_AVAILABLE:
        return None
    
    try:
        init_cloudinary()
        result = cloudinary.uploader.upload(
            file,
            folder=f"edo_odyssey/{folder}",
            use_filename=True,
            unique_filename=True,
            overwrite=True,
            resource_type="image",
            transformation=[
                {'width': 1200, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ]
        )
        return result.get('secure_url')
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None

def delete_from_cloudinary(public_id):
    """Delete a file from Cloudinary"""
    if not CLOUDINARY_AVAILABLE:
        return False
    
    try:
        init_cloudinary()
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return False

def get_cloudinary_url(public_id, options=None):
    """Get a Cloudinary URL with transformations"""
    if not CLOUDINARY_AVAILABLE:
        return None
    
    try:
        init_cloudinary()
        if options:
            return cloudinary.utils.cloudinary_url(public_id, **options)[0]
        return cloudinary.utils.cloudinary_url(public_id)[0]
    except Exception as e:
        print(f"Cloudinary URL error: {e}")
        return None

def save_uploaded_file(file, folder="attractions", resize=True, max_width=1200, max_height=800, quality=85):
    """
    Save an uploaded file to the appropriate folder and return the URL path.
    Automatically resizes and optimizes images.
    """
    if not file or not file.filename:
        return None
    
    # Check if we should use Cloudinary (for production/Vercel)
    use_cloudinary = current_app.config.get('CLOUDINARY_CLOUD_NAME')
    
    if use_cloudinary:
        # Upload to Cloudinary
        return upload_to_cloudinary(file, folder)
    
    # Local storage fallback
    # Create directory if it doesn't exist
    upload_folder = current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, "static/uploads"))
    folder_path = os.path.join(upload_folder, folder)
    os.makedirs(folder_path, exist_ok=True)
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'png'
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(folder_path, filename)
    
    # Save the file
    file.save(filepath)
    
    # Resize and optimize images
    if resize and ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        try:
            img = Image.open(filepath)
            
            # Convert RGBA to RGB for JPEG
            if ext in ['jpg', 'jpeg'] and img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Resize if too large
            width, height = img.size
            if width > max_width or height > max_height:
                ratio = min(max_width/width, max_height/height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save with optimization
            if ext in ['jpg', 'jpeg']:
                img.save(filepath, 'JPEG', quality=quality, optimize=True)
            elif ext == 'png':
                img.save(filepath, 'PNG', optimize=True)
            elif ext == 'webp':
                img.save(filepath, 'WEBP', quality=quality)
            else:
                img.save(filepath)
                
        except Exception as e:
            print(f"Image optimization error: {e}")
    
    # Return the URL path for the file
    return f"/static/uploads/{folder}/{filename}"

def delete_uploaded_file(file_url, folder="attractions"):
    """Delete an uploaded file from the filesystem or Cloudinary"""
    if not file_url:
        return False
    
    # Check if it's a Cloudinary URL
    if CLOUDINARY_AVAILABLE and 'cloudinary' in file_url:
        try:
            # Extract public_id from URL
            # Example: https://res.cloudinary.com/cloud_name/image/upload/v123456/edo_odyssey/attractions/filename.jpg
            parts = file_url.split('/')
            # Get the part after 'upload/'
            upload_index = -1
            for i, part in enumerate(parts):
                if part == 'upload':
                    upload_index = i
                    break
            
            if upload_index != -1 and upload_index + 1 < len(parts):
                public_id = '/'.join(parts[upload_index + 1:]).split('.')[0]
                return delete_from_cloudinary(public_id)
        except Exception as e:
            print(f"Cloudinary delete error: {e}")
    
    # Local file deletion
    filename = os.path.basename(file_url)
    upload_folder = current_app.config.get("UPLOAD_FOLDER", os.path.join(current_app.root_path, "static/uploads"))
    filepath = os.path.join(upload_folder, folder, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def slugify(text):
    """Convert text to a URL-friendly slug"""
    if not text:
        return ""
    text = text.lower()
    # Replace spaces with hyphens
    text = text.replace(' ', '-')
    # Remove special characters
    text = ''.join(c for c in text if c.isalnum() or c == '-')
    # Remove multiple hyphens
    while '--' in text:
        text = text.replace('--', '-')
    return text.strip('-')

def log_action(action, module="general", record_id=None, details=None):
    """Log an admin action to the audit log"""
    from flask_login import current_user
    
    try:
        # Get user email or use a default
        user_email = None
        user_role = "System"
        
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user_email = current_user.email
            user_role = getattr(current_user, 'role', 'User')
        
        # If no user is logged in, use a system email
        if not user_email:
            user_email = "system@edo-odyssey.com"
        
        log = AuditLog(
            user_id=current_user.id if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated else None,
            operator_email=user_email,
            role=user_role,
            action=action,
            module=module,
            record_id=record_id,
            ip_address=request.remote_addr if request else '127.0.0.1',
            user_agent=request.headers.get('User-Agent', '') if request else '',
            created_at=datetime.utcnow(),
            status='active'
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # If logging fails, just print the error but don't break the app
        print(f"Logging error: {e}")
        db.session.rollback()
    return log

def generate_reference_code(prefix="BK"):
    """Generate a unique reference code"""
    import random
    import string
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{timestamp}-{random_part}"

# Alias for generate_reference_code to maintain compatibility
def generate_reference(prefix="BK"):
    """Alias for generate_reference_code"""
    return generate_reference_code(prefix)

def create_notification(user_id, title, message, notif_type="info", link=None):
    """Create a notification for a user"""
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
            link=link,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        print(f"Notification creation error: {e}")
        db.session.rollback()
        return None

def award_heritage_points(user, activity_type, points=0):
    """
    Award heritage points to a user based on activity type.
    
    Activity types and default points:
    - 'review': 10 points
    - 'booking': 20 points
    - 'favourite': 5 points
    - 'tour_completed': 30 points
    - 'referral': 50 points
    - 'attraction_visit': 15 points
    - 'event_attendance': 25 points
    - 'guide_request': 10 points
    """
    point_map = {
        'review': 10,
        'booking': 20,
        'favourite': 5,
        'tour_completed': 30,
        'referral': 50,
        'attraction_visit': 15,
        'event_attendance': 25,
        'guide_request': 10,
    }
    
    # If points are specified directly, use that
    if points > 0:
        award_points = points
    else:
        award_points = point_map.get(activity_type, 0)
    
    if award_points > 0 and user:
        user.heritage_points = (user.heritage_points or 0) + award_points
        db.session.commit()
        
        # Create notification for the user
        create_notification(
            user_id=user.id,
            title="🎉 Heritage Points Earned!",
            message=f"You earned {award_points} Heritage Points for {activity_type.replace('_', ' ').title()}!",
            notif_type="success",
            link="/dashboard"
        )
        
        return award_points
    return 0

def format_currency(amount, currency="₦"):
    """Format currency amount"""
    if amount is None:
        return f"{currency}0"
    return f"{currency}{amount:,.2f}"

def get_file_size(filepath):
    """Get file size in a human-readable format"""
    if not os.path.exists(filepath):
        return "0 B"
    
    size = os.path.getsize(filepath)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"