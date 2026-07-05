from flask import Blueprint, render_template, request
from ..models.models import Restaurant, Review, RestaurantMenu

restaurants_bp = Blueprint("restaurants", __name__, url_prefix="/restaurants")


@restaurants_bp.route("/")
def list_restaurants():
    page = request.args.get("page", 1, type=int)
    search_q = request.args.get("q", "").strip()
    cuisine = request.args.get("cuisine", "").strip()
    sort = request.args.get("sort", "name")

    query = Restaurant.query.filter_by(status="active")
    if search_q:
        query = query.filter(Restaurant.name.ilike(f"%{search_q}%"))
    if cuisine:
        query = query.filter(Restaurant.cuisine.ilike(f"%{cuisine}%"))
    if sort == "price_asc":
        query = query.order_by(Restaurant.price_range.asc())
    else:
        query = query.order_by(Restaurant.name.asc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    cuisines = [r.cuisine for r in Restaurant.query.with_entities(Restaurant.cuisine).distinct().all()]
    return render_template(
        "restaurants/list.html",
        restaurants=pagination.items,
        pagination=pagination,
        cuisines=cuisines,
        search_q=search_q,
        selected_cuisine=cuisine,
        sort=sort,
    )


@restaurants_bp.route("/<int:id>")
def detail(id):
    restaurant = Restaurant.query.filter_by(id=id, status="active").first_or_404()
    reviews = Review.query.filter_by(target_type="Restaurant", target_id=id, is_approved=True).order_by(Review.created_at.desc()).all()
    menus = RestaurantMenu.query.filter_by(restaurant_id=id, available=True).all()
    return render_template("restaurants/detail.html", restaurant=restaurant, reviews=reviews, menus=menus)
