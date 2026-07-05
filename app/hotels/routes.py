from flask import Blueprint, render_template, request
from ..models.models import Hotel, Review, HotelRoom

hotels_bp = Blueprint("hotels", __name__, url_prefix="/hotels")


@hotels_bp.route("/")
def list_hotels():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    stars = request.args.get("stars", type=int)
    sort = request.args.get("sort", "name")

    query = Hotel.query.filter_by(status="active")
    if search_q:
        query = query.filter(Hotel.name.ilike(f"%{search_q}%"))
    if stars:
        query = query.filter_by(stars=stars)
    if sort == "price_asc":
        query = query.order_by(Hotel.price_per_night.asc())
    elif sort == "price_desc":
        query = query.order_by(Hotel.price_per_night.desc())
    elif sort == "stars":
        query = query.order_by(Hotel.stars.desc())
    else:
        query = query.order_by(Hotel.name.asc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    return render_template(
        "hotels/list.html",
        hotels=pagination.items,
        pagination=pagination,
        search_q=search_q,
        selected_stars=stars,
        sort=sort,
    )


@hotels_bp.route("/<int:id>")
def detail(id):
    hotel = Hotel.query.filter_by(id=id, status="active").first_or_404()
    reviews = Review.query.filter_by(target_type="Hotel", target_id=id, is_approved=True).order_by(Review.created_at.desc()).all()
    rooms = HotelRoom.query.filter_by(hotel_id=id, available=True).all()
    return render_template("hotels/detail.html", hotel=hotel, reviews=reviews, rooms=rooms)
