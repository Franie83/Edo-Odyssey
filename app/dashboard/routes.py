from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.models import Booking, Review, Notification, Favourite, Attraction, Hotel, Restaurant, Guide, Event
from ..extensions import db
from ..utils.helpers import log_action, save_uploaded_file, allowed_file, award_heritage_points

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    # Get bookings made BY the user (as a tourist)
    user_bookings = Booking.query.filter_by(
        user_id=current_user.id, 
        status="active"
    ).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get bookings WHERE the user is the TARGET (Guide/Hotel/Restaurant/Attraction owner)
    target_bookings = []
    
    if current_user.role == "Guide":
        # Find all guides for this user
        guides = Guide.query.filter_by(user_id=current_user.id).all()
        guide_ids = [g.id for g in guides]
        if guide_ids:
            target_bookings = Booking.query.filter(
                Booking.booking_type == "Guide",
                Booking.target_id.in_(guide_ids),
                Booking.status == "active"
            ).order_by(Booking.created_at.desc()).limit(10).all()
    
    elif current_user.role == "Hotel":
        hotels = Hotel.query.filter_by(user_id=current_user.id).all()
        hotel_ids = [h.id for h in hotels]
        if hotel_ids:
            target_bookings = Booking.query.filter(
                Booking.booking_type == "Hotel",
                Booking.target_id.in_(hotel_ids),
                Booking.status == "active"
            ).order_by(Booking.created_at.desc()).limit(10).all()
    
    elif current_user.role == "Restaurant":
        restaurants = Restaurant.query.filter_by(user_id=current_user.id).all()
        restaurant_ids = [r.id for r in restaurants]
        if restaurant_ids:
            target_bookings = Booking.query.filter(
                Booking.booking_type == "Restaurant",
                Booking.target_id.in_(restaurant_ids),
                Booking.status == "active"
            ).order_by(Booking.created_at.desc()).limit(10).all()
    
    elif current_user.role in ["Agency Admin", "Super Admin"]:
        target_bookings = Booking.query.filter(
            Booking.status == "active"
        ).order_by(Booking.created_at.desc()).limit(10).all()
    
    # Combine bookings (user's bookings + target bookings)
    all_bookings = list(user_bookings) + list(target_bookings)
    # Remove duplicates and sort by created_at
    seen_ids = set()
    unique_bookings = []
    for b in sorted(all_bookings, key=lambda x: x.created_at, reverse=True):
        if b.id not in seen_ids:
            seen_ids.add(b.id)
            unique_bookings.append(b)
    
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).limit(5).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    favourites = Favourite.query.filter_by(user_id=current_user.id).limit(6).all()

    # Stats
    total_bookings = Booking.query.filter_by(user_id=current_user.id, status="active").count()
    total_target_bookings = len(target_bookings)
    
    # Count pending bookings from both user and target
    user_pending = Booking.query.filter_by(user_id=current_user.id, booking_status="Pending").count()
    target_pending = len([b for b in target_bookings if b.booking_status == "Pending" or b.booking_status == "Approved"])
    
    # Count completed bookings from both user and target
    user_completed = Booking.query.filter_by(user_id=current_user.id, booking_status="Completed").count()
    target_completed = len([b for b in target_bookings if b.booking_status == "Completed"])
    
    stats = {
        "total_bookings": total_bookings + total_target_bookings,
        "pending_bookings": user_pending + target_pending,
        "completed_bookings": user_completed + target_completed,
        "total_reviews": Review.query.filter_by(user_id=current_user.id).count(),
        "heritage_points": current_user.heritage_points,
    }

    guide_profile = None
    if current_user.role == "Guide":
        guide_profile = Guide.query.filter_by(user_id=current_user.id).first()

    return render_template(
        "dashboard/index.html",
        bookings=unique_bookings,
        reviews=reviews,
        notifications=notifications,
        favourites=favourites,
        stats=stats,
        guide_profile=guide_profile,
    )


@dashboard_bp.route("/notifications/read/<int:id>", methods=["POST"])
@login_required
def mark_read(id):
    notif = Notification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/notifications/read-all", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        current_user.first_name = request.form.get("first_name", current_user.first_name).strip()
        current_user.last_name = request.form.get("last_name", current_user.last_name).strip()
        current_user.phone = request.form.get("phone", current_user.phone or "").strip()
        current_user.bio = request.form.get("bio", "").strip()
        current_user.address = request.form.get("address", "").strip()
        current_user.nationality = request.form.get("nationality", "").strip()

        avatar = request.files.get("avatar")
        if avatar and allowed_file(avatar.filename):
            url = save_uploaded_file(avatar, "users")
            current_user.avatar_url = url

        new_pass = request.form.get("new_password", "")
        if new_pass:
            if len(new_pass) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return redirect(url_for("dashboard.profile"))
            current_user.set_password(new_pass)

        db.session.commit()
        log_action("Updated profile", module="dashboard")
        flash("Profile updated successfully.", "success")
        return redirect(url_for("dashboard.profile"))

    return render_template("dashboard/profile.html")


@dashboard_bp.route("/favourite/<target_type>/<int:target_id>", methods=["POST"])
@login_required
def toggle_favourite(target_type, target_id):
    existing = Favourite.query.filter_by(user_id=current_user.id, target_type=target_type, target_id=target_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Removed from favourites.", "info")
    else:
        fav = Favourite(user_id=current_user.id, target_type=target_type, target_id=target_id)
        db.session.add(fav)
        db.session.commit()
        
        # Award heritage points for favouriting
        award_heritage_points(current_user, 'favourite')
        flash("Added to favourites! You earned 5 Heritage Points! 🎉", "success")
        
    return redirect(request.referrer or url_for("dashboard.index"))


@dashboard_bp.route("/bookings/<int:id>")
@login_required
def booking_detail(id):
    booking = Booking.query.get_or_404(id)
    
    # Check if user has access to this booking (either they made it or they are the target)
    if booking.user_id != current_user.id:
        # Check if user is the target
        if not is_booking_target(current_user, booking):
            flash("You do not have access to this booking.", "danger")
            return redirect(url_for("dashboard.index"))
    
    return render_template("dashboard/booking_detail.html", booking=booking)


# ─── CONTEXT PROCESSOR FOR TEMPLATES ──────────────────────────────
@dashboard_bp.context_processor
def utility_processor():
    def is_booking_target(user, booking):
        """Check if a user is the target of a booking"""
        if not user or not booking:
            return False
        
        try:
            if booking.booking_type == "Guide":
                guide = Guide.query.get(booking.target_id)
                return guide and guide.user_id == user.id
            elif booking.booking_type == "Hotel":
                hotel = Hotel.query.get(booking.target_id)
                return hotel and hotel.user_id == user.id
            elif booking.booking_type == "Tour":
                attraction = Attraction.query.get(booking.target_id)
                return attraction and attraction.user_id == user.id
            elif booking.booking_type == "Event":
                event = Event.query.get(booking.target_id)
                return event and event.user_id == user.id
            return False
        except Exception:
            return False
    
    def get_booking_target_name(booking):
        """Get the name of the target for a booking"""
        if not booking:
            return "Unknown"
        
        try:
            if booking.booking_type == "Guide":
                guide = Guide.query.get(booking.target_id)
                return guide.user.full_name if guide and guide.user else booking.target_name
            elif booking.booking_type == "Hotel":
                hotel = Hotel.query.get(booking.target_id)
                return hotel.name if hotel else booking.target_name
            elif booking.booking_type == "Tour":
                attraction = Attraction.query.get(booking.target_id)
                return attraction.name if attraction else booking.target_name
            elif booking.booking_type == "Event":
                event = Event.query.get(booking.target_id)
                return event.name if event else booking.target_name
            return booking.target_name or "Unknown"
        except Exception:
            return booking.target_name or "Unknown"
    
    return dict(
        is_booking_target=is_booking_target,
        get_booking_target_name=get_booking_target_name
    )