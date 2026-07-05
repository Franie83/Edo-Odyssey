from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.models import Booking, Review, Notification, Favourite, Attraction, Hotel, Restaurant, Guide
from ..extensions import db
from ..utils.helpers import log_action, save_uploaded_file, allowed_file

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/")
@login_required
def index():
    bookings = Booking.query.filter_by(user_id=current_user.id, status="active").order_by(Booking.created_at.desc()).limit(10).all()
    reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).limit(5).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()
    favourites = Favourite.query.filter_by(user_id=current_user.id).limit(6).all()

    stats = {
        "total_bookings": Booking.query.filter_by(user_id=current_user.id, status="active").count(),
        "pending_bookings": Booking.query.filter_by(user_id=current_user.id, booking_status="Pending").count(),
        "completed_bookings": Booking.query.filter_by(user_id=current_user.id, booking_status="Completed").count(),
        "total_reviews": Review.query.filter_by(user_id=current_user.id).count(),
        "heritage_points": current_user.heritage_points,
    }

    guide_profile = None
    if current_user.role == "Guide":
        guide_profile = Guide.query.filter_by(user_id=current_user.id).first()

    return render_template(
        "dashboard/index.html",
        bookings=bookings,
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
        flash("Added to favourites!", "success")
    return redirect(request.referrer or url_for("dashboard.index"))
