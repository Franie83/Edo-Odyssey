from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.models import Booking, Hotel, Guide, Attraction, Event
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

        # Create notification
        create_notification(
            current_user.id,
            "🎫 Booking Confirmed!",
            f"Your {booking_type} booking (Ref: {ref}) has been submitted. You earned {points_earned} Heritage Points! Total: ₦{price:,.0f}",
            "success",
            link="/dashboard",
        )
        
        log_action(f"Created {booking_type} booking #{booking.id} (Ref:{ref})", module="bookings", record_id=booking.id)
        flash(f"Booking submitted! Reference: {ref}. Total: ₦{price:,.0f}. You earned {points_earned} Heritage Points! 🎉", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("bookings/new.html", booking_type=booking_type, target=target, target_id=target_id)


@bookings_bp.route("/<int:id>/cancel", methods=["POST"])
@login_required
def cancel_booking(id):
    booking = Booking.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if booking.booking_status in ("Completed", "Cancelled"):
        flash("Cannot cancel this booking.", "warning")
        return redirect(url_for("dashboard.index"))
    reason = request.form.get("reason", "Cancelled by user")
    booking.booking_status = "Cancelled"
    booking.cancellation_reason = reason
    db.session.commit()
    log_action(f"Cancelled booking #{id}", module="bookings", record_id=id)
    flash("Booking cancelled.", "info")
    return redirect(url_for("dashboard.index"))