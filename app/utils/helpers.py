import os
import uuid
import hashlib
from datetime import datetime
from flask import current_app, url_for, request
from werkzeug.utils import secure_filename
from PIL import Image
from ..extensions import db
from ..models.models import AuditLog, Notification

def allowed_file(filename):
    """Check if the file extension is allowed"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, folder="attractions", resize=True, max_width=1200, max_height=800, quality=85):
    """
    Save an uploaded file to the appropriate folder and return the URL path.
    Automatically resizes and optimizes images.
    """
    if not file or not file.filename:
        return None
    
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
    """Delete an uploaded file from the filesystem"""
    if not file_url:
        return False
    
    # Extract filename from URL
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