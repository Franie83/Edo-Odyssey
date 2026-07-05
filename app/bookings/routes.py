from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.models import Booking, Hotel, Guide, Attraction, Event, User, Notification
from ..extensions import db
from ..utils.helpers import log_action, generate_reference_code, create_notification, award_heritage_points

bookings_bp = Blueprint("bookings", __name__, url_prefix="/bookings")


def _resolve_target_name(btype, tid):
    mapping = {"Hotel": Hotel, "Guide": Guide, "Tour": Attraction, "Event": Event}
    model = mapping.get(btype)
    if not model:
        return btype
    obj = model.query.get(tid)
    if not obj:
        return btype
    if btype == "Guide":
        return obj.user.full_name if obj.user else "Guide"
    return obj.name


@bookings_bp.route("/new/<booking_type>/<int:target_id>", methods=["GET", "POST"])
@login_required
def new_booking(booking_type, target_id):
    allowed = ["Hotel", "Guide", "Tour", "Event"]
    if booking_type not in allowed:
        flash("Invalid booking type.", "danger")
        return redirect(url_for("main.home"))

    # Resolve target object
    target = None
    if booking_type == "Hotel":
        target = Hotel.query.get_or_404(target_id)
    elif booking_type == "Guide":
        target = Guide.query.get_or_404(target_id)
    elif booking_type == "Tour":
        target = Attraction.query.get_or_404(target_id)
    elif booking_type == "Event":
        target = Event.query.get_or_404(target_id)

    if request.method == "POST":
        start_str = request.form.get("start_date", "")
        end_str = request.form.get("end_date", "")
        guests = int(request.form.get("num_guests", 1))
        notes = request.form.get("notes", "")

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d") if end_str else None
        except ValueError:
            flash("Invalid date format.", "danger")
            return render_template("bookings/new.html", booking_type=booking_type, target=target, target_id=target_id)

        # Calculate price
        price = 0.0
        if booking_type == "Hotel":
            nights = (end_date - start_date).days if end_date else 1
            price = target.price_per_night * max(1, nights) * guests
        elif booking_type == "Guide":
            days = (end_date - start_date).days if end_date else 1
            price = target.daily_rate * max(1, days)
        elif booking_type == "Tour":
            price = target.ticket_price * guests
        elif booking_type == "Event":
            price = target.ticket_price * guests

        ref = generate_reference_code()
        booking = Booking(
            user_id=current_user.id,
            booking_type=booking_type,
            target_id=target_id,
            target_name=_resolve_target_name(booking_type, target_id),
            start_date=start_date,
            end_date=end_date,
            total_price=price,
            booking_status="Pending",
            reference_code=ref,
            num_guests=guests,
            notes=notes,
            status="active",
        )
        db.session.add(booking)
        db.session.commit()

        # 🎯 AWARD HERITAGE POINTS - 20 points for making a booking
        points_earned = award_heritage_points(current_user, 'booking')

        # Create notification for user
        create_notification(
            current_user.id,
            "🎫 Booking Submitted!",
            f"Your {booking_type} booking (Ref: {ref}) has been submitted. You earned {points_earned} Heritage Points! Total: ₦{price:,.0f}",
            "success",
            link="/dashboard",
        )

        # Notify admin about new booking
        admins = User.query.filter(User.role.in_(['Agency Admin', 'Super Admin'])).all()
        for admin in admins:
            create_notification(
                admin.id,
                "📋 New Booking Pending",
                f"New {booking_type} booking (Ref: {ref}) from {current_user.full_name} for {booking.target_name}. Please review and approve.",
                "info",
                link="/admin/bookings"
            )
        
        log_action(f"Created {booking_type} booking #{booking.id} (Ref:{ref})", module="bookings", record_id=booking.id)
        flash(f"Booking submitted! Reference: {ref}. Total: ₦{price:,.0f}. You earned {points_earned} Heritage Points! 🎉", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("bookings/new.html", booking_type=booking_type, target=target, target_id=target_id)


@bookings_bp.route("/<int:id>/cancel", methods=["POST"])
@login_required
def cancel_booking(id):
    booking = Booking.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if booking.booking_status in ("Completed", "Cancelled", "Approved", "Confirmed"):
        flash("Cannot cancel this booking at this stage.", "warning")
        return redirect(url_for("dashboard.index"))
    reason = request.form.get("reason", "Cancelled by user")
    booking.booking_status = "Cancelled"
    booking.cancellation_reason = reason
    db.session.commit()
    log_action(f"Cancelled booking #{id}", module="bookings", record_id=id)
    flash("Booking cancelled.", "info")
    return redirect(url_for("dashboard.index"))


@bookings_bp.route("/<int:id>/target-confirm", methods=["POST"])
@login_required
def target_confirm_booking(id):
    """Target (Guide/Hotel/etc.) confirms the booking"""
    booking = Booking.query.get_or_404(id)
    
    # Check if current user is the target
    if not _is_booking_target(current_user, booking):
        flash("You are not authorized to confirm this booking.", "danger")
        return redirect(url_for("dashboard.index"))
    
    if booking.booking_status != "Approved":
        flash("This booking must be approved by admin first.", "warning")
        return redirect(url_for("dashboard.index"))
    
    comment = request.form.get("target_comment", "").strip()
    
    booking.booking_status = "Confirmed"
    booking.confirmed_at = datetime.utcnow()
    booking.target_comment = comment
    db.session.commit()
    
    # Notify the user
    create_notification(
        booking.user_id,
        "✅ Booking Confirmed!",
        f"Your booking {booking.reference_code} for {booking.target_name} has been confirmed.",
        "success",
        link=f"/dashboard/bookings/{booking.id}"
    )
    
    flash("Booking confirmed successfully!", "success")
    return redirect(url_for("dashboard.index"))


@bookings_bp.route("/<int:id>/target-reject", methods=["POST"])
@login_required
def target_reject_booking(id):
    """Target (Guide/Hotel/etc.) rejects the booking"""
    booking = Booking.query.get_or_404(id)
    
    # Check if current user is the target
    if not _is_booking_target(current_user, booking):
        flash("You are not authorized to reject this booking.", "danger")
        return redirect(url_for("dashboard.index"))
    
    if booking.booking_status != "Approved":
        flash("This booking must be approved by admin first.", "warning")
        return redirect(url_for("dashboard.index"))
    
    reason = request.form.get("rejection_reason", "Booking rejected by service provider").strip()
    
    booking.booking_status = "Rejected"
    booking.target_comment = reason
    db.session.commit()
    
    # Notify the user
    create_notification(
        booking.user_id,
        "❌ Booking Rejected",
        f"Your booking {booking.reference_code} for {booking.target_name} has been rejected. Reason: {reason}",
        "danger",
        link=f"/dashboard/bookings/{booking.id}"
    )
    
    flash("Booking rejected.", "info")
    return redirect(url_for("dashboard.index"))


@bookings_bp.route("/<int:id>/complete", methods=["POST"])
@login_required
def complete_booking(id):
    """Mark booking as completed (after service is rendered)"""
    booking = Booking.query.get_or_404(id)
    
    # Check if current user is the target
    if not _is_booking_target(current_user, booking):
        flash("You are not authorized to complete this booking.", "danger")
        return redirect(url_for("dashboard.index"))
    
    if booking.booking_status != "Confirmed":
        flash("Booking must be confirmed before completing.", "warning")
        return redirect(url_for("dashboard.index"))
    
    booking.booking_status = "Completed"
    booking.completed_at = datetime.utcnow()
    db.session.commit()
    
    # Award heritage points to the user
    user = User.query.get(booking.user_id)
    if user:
        award_heritage_points(user, 'tour_completed')
    
    # Notify the user
    create_notification(
        booking.user_id,
        "🎉 Booking Completed!",
        f"Your booking {booking.reference_code} for {booking.target_name} has been completed. You earned 30 Heritage Points!",
        "success",
        link=f"/dashboard/bookings/{booking.id}"
    )
    
    flash("Booking marked as completed!", "success")
    return redirect(url_for("dashboard.index"))


def _is_booking_target(user, booking):
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