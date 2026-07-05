"""REST API endpoints (JSON) — Flask Blueprint."""
from flask import Blueprint, jsonify, request
from ..models.models import Attraction, Guide, Hotel, Restaurant, Event, News, Booking, Review
from ..extensions import db
from flask_login import current_user, login_required

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Edo Odyssey API"})


@api_bp.route("/attractions")
def api_attractions():
    items = Attraction.query.filter_by(active=True, status="active").limit(50).all()
    return jsonify([{
        "id": a.id, "name": a.name, "description": a.description[:200],
        "latitude": a.latitude, "longitude": a.longitude,
        "ticket_price": a.ticket_price, "image_url": a.image_url,
        "featured": a.featured, "avg_rating": a.avg_rating,
    } for a in items])


@api_bp.route("/guides")
def api_guides():
    items = Guide.query.filter_by(verification_status="Approved", status="active").all()
    return jsonify([{
        "id": g.id, "name": g.user.full_name if g.user else "",
        "languages": g.languages, "experience": g.experience,
        "hourly_rate": g.hourly_rate, "daily_rate": g.daily_rate,
        "availability": g.availability, "avg_rating": g.avg_rating,
    } for g in items])


@api_bp.route("/hotels")
def api_hotels():
    items = Hotel.query.filter_by(status="active").all()
    return jsonify([{
        "id": h.id, "name": h.name, "address": h.address,
        "price_per_night": h.price_per_night, "stars": h.stars,
        "latitude": h.latitude, "longitude": h.longitude,
        "image_url": h.image_url, "avg_rating": h.avg_rating,
    } for h in items])


@api_bp.route("/events")
def api_events():
    from datetime import datetime
    items = Event.query.filter_by(active=True, status="active").filter(Event.date >= datetime.utcnow()).order_by(Event.date).all()
    return jsonify([{
        "id": e.id, "name": e.name, "date": e.date.isoformat(),
        "location": e.location, "ticket_price": e.ticket_price,
        "image_url": e.image_url, "days_until": e.days_until,
    } for e in items])


@api_bp.route("/search")
def api_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": []})
    like = f"%{q}%"
    attractions = [{"type": "attraction", "id": a.id, "name": a.name} for a in Attraction.query.filter(Attraction.name.ilike(like), Attraction.status == "active").limit(5).all()]
    hotels = [{"type": "hotel", "id": h.id, "name": h.name} for h in Hotel.query.filter(Hotel.name.ilike(like), Hotel.status == "active").limit(5).all()]
    return jsonify({"query": q, "results": attractions + hotels})


@api_bp.route("/stats")
def api_stats():
    return jsonify({
        "total_attractions": Attraction.query.filter_by(status="active").count(),
        "total_guides": Guide.query.filter_by(verification_status="Approved", status="active").count(),
        "total_hotels": Hotel.query.filter_by(status="active").count(),
        "total_restaurants": Restaurant.query.filter_by(status="active").count(),
        "total_events": Event.query.filter_by(status="active").count(),
        "total_bookings": Booking.query.filter_by(status="active").count(),
        "total_reviews": Review.query.filter_by(status="active").count(),
    })
