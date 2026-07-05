from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from ..models.models import Review, Attraction, Guide, Hotel, Restaurant
from ..extensions import db
from ..utils.helpers import log_action, create_notification, award_heritage_points

reviews_bp = Blueprint("reviews", __name__, url_prefix="/reviews")


@reviews_bp.route("/add/<target_type>/<int:target_id>", methods=["POST"])
@login_required
def add_review(target_type, target_id):
    allowed = ["Attraction", "Hotel", "Guide", "Restaurant"]
    if target_type not in allowed:
        flash("Invalid review target.", "danger")
        return redirect(url_for("main.home"))

    rating = int(request.form.get("rating", 5))
    comment = request.form.get("comment", "").strip()
    redirect_url = request.form.get("redirect_url", url_for("main.home"))

    if not (1 <= rating <= 5) or not comment:
        flash("Please provide a valid rating and comment.", "warning")
        return redirect(redirect_url)

    # Check if already reviewed
    existing = Review.query.filter_by(
        user_id=current_user.id, target_type=target_type, target_id=target_id
    ).first()
    
    if existing:
        existing.rating = rating
        existing.comment = comment
        existing.updated_at = db.func.now()
        db.session.commit()
        flash("Your review has been updated.", "success")
        log_action(f"Updated {rating}-star review on {target_type} #{target_id}", module="reviews")
    else:
        review = Review(
            user_id=current_user.id,
            target_type=target_type,
            target_id=target_id,
            rating=rating,
            comment=comment,
            is_approved=True,
            status="active",
        )
        db.session.add(review)
        db.session.commit()
        
        # 🎯 AWARD HERITAGE POINTS - 10 points for writing a review
        points_earned = award_heritage_points(current_user, 'review')
        
        # Get target name for the notification
        target_name = _get_target_name(target_type, target_id)
        
        # Create notification
        create_notification(
            current_user.id,
            "📝 Review Submitted!",
            f"You earned {points_earned} Heritage Points for your review on {target_name}!",
            "success",
            link="/dashboard"
        )
        
        flash(f"Review submitted! You earned {points_earned} Heritage Points! 🎉", "success")
        log_action(f"Submitted {rating}-star review on {target_type} #{target_id}", module="reviews")

    return redirect(redirect_url)


def _get_target_name(target_type, target_id):
    """Get the name of the target entity"""
    try:
        if target_type == "Attraction":
            target = Attraction.query.get(target_id)
            return target.name if target else "Attraction"
        elif target_type == "Guide":
            target = Guide.query.get(target_id)
            return target.user.full_name if target and target.user else "Guide"
        elif target_type == "Hotel":
            target = Hotel.query.get(target_id)
            return target.name if target else "Hotel"
        elif target_type == "Restaurant":
            target = Restaurant.query.get(target_id)
            return target.name if target else "Restaurant"
        return target_type
    except:
        return target_type


@reviews_bp.route("/<int:id>/helpful", methods=["POST"])
@login_required
def mark_helpful(id):
    """Mark a review as helpful"""
    review = Review.query.get_or_404(id)
    
    # Prevent users from marking their own review as helpful
    if review.user_id == current_user.id:
        flash("You cannot mark your own review as helpful.", "warning")
        return redirect(request.referrer or url_for("main.home"))
    
    review.helpful_count = (review.helpful_count or 0) + 1
    db.session.commit()
    
    # Award points for marking a review as helpful (optional)
    # points_earned = award_heritage_points(current_user, 'helpful')
    
    flash("Thank you for marking this review as helpful! 🙌", "success")
    return redirect(request.referrer or url_for("main.home"))


@reviews_bp.route("/<int:id>/report", methods=["POST"])
@login_required
def report_review(id):
    """Report a review for moderation"""
    review = Review.query.get_or_404(id)
    
    # In a real implementation, you'd create a Report model
    # For now, just log it and notify admin
    log_action(
        f"User {current_user.id} reported review #{id}", 
        module="reviews", 
        record_id=id
    )
    
    flash("Thank you for reporting this review. Our team will review it.", "info")
    return redirect(request.referrer or url_for("main.home"))


@reviews_bp.route("/my-reviews")
@login_required
def my_reviews():
    """View all reviews by the current user"""
    page = request.args.get("page", 1, type=int)
    reviews = Review.query.filter_by(
        user_id=current_user.id,
        status="active"
    ).order_by(Review.created_at.desc()).paginate(page=page, per_page=10)
    
    return render_template("reviews/my_reviews.html", reviews=reviews)