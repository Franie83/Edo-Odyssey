from flask import Blueprint, render_template, request, abort, current_app
from ..models.models import Attraction, Category, Review, QRCode
from ..extensions import db
import os

attractions_bp = Blueprint("attractions", __name__, url_prefix="/attractions")


@attractions_bp.route("/")
def list_attractions():
    page = request.args.get("page", 1, type=int)
    category_id = request.args.get("category", type=int)
    search_q = request.args.get("q", "").strip()
    featured_only = request.args.get("featured", "")
    sort = request.args.get("sort", "name")

    query = Attraction.query.filter_by(active=True, status="active")
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search_q:
        query = query.filter(Attraction.name.ilike(f"%{search_q}%"))
    if featured_only:
        query = query.filter_by(featured=True)
    if sort == "price_asc":
        query = query.order_by(Attraction.ticket_price.asc())
    elif sort == "price_desc":
        query = query.order_by(Attraction.ticket_price.desc())
    elif sort == "views":
        query = query.order_by(Attraction.views.desc())
    else:
        query = query.order_by(Attraction.name.asc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    categories = Category.query.filter_by(type="attraction", status="active").all()
    return render_template(
        "attractions/list.html",
        attractions=pagination.items,
        pagination=pagination,
        categories=categories,
        current_category=category_id,
        search_q=search_q,
        sort=sort,
    )


@attractions_bp.route("/<int:id>")
def detail(id):
    attraction = Attraction.query.filter_by(id=id, active=True).first_or_404()
    # Increment view count
    attraction.views = (attraction.views or 0) + 1
    db.session.commit()

    reviews = Review.query.filter_by(target_type="Attraction", target_id=id, is_approved=True).order_by(Review.created_at.desc()).all()
    qr = QRCode.query.filter_by(attraction_id=id).first()
    
    # Check if QR code file actually exists
    qr_exists = False
    if qr and qr.code:
        qr_path = os.path.join(current_app.root_path, 'static/uploads/qr_codes', qr.code)
        qr_exists = os.path.exists(qr_path)
        
        # If QR code record exists but file doesn't, generate a new one
        if not qr_exists:
            from ..utils.qr_utils import generate_qr_code
            qr_exists = generate_qr_code(id) is not None
            if qr_exists:
                # Refresh the QR code record
                qr = QRCode.query.filter_by(attraction_id=id).first()
    
    nearby = Attraction.query.filter(
        Attraction.id != id, 
        Attraction.active == True, 
        Attraction.status == "active",
        Attraction.latitude.isnot(None),
        Attraction.longitude.isnot(None),
        Attraction.latitude.between(attraction.latitude - 0.05 if attraction.latitude else -90, 
                                   attraction.latitude + 0.05 if attraction.latitude else 90),
        Attraction.longitude.between(attraction.longitude - 0.05 if attraction.longitude else -180, 
                                    attraction.longitude + 0.05 if attraction.longitude else 180)
    ).limit(3).all()
    
    return render_template(
        "attractions/detail.html",
        attraction=attraction,
        reviews=reviews,
        qr=qr,
        qr_exists=qr_exists,
        nearby=nearby,
    )