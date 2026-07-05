from flask import Blueprint, render_template, request
from ..models.models import Attraction, Hotel, Restaurant, Guide, Event, News

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/")
def results():
    q = request.args.get("q", "").strip()
    if not q:
        return render_template("search/results.html", q=q, results={}, total=0)

    like = f"%{q}%"
    attractions = Attraction.query.filter(Attraction.name.ilike(like), Attraction.active == True, Attraction.status == "active").limit(5).all()
    hotels = Hotel.query.filter(Hotel.name.ilike(like), Hotel.status == "active").limit(5).all()
    restaurants = Restaurant.query.filter(Restaurant.name.ilike(like), Restaurant.status == "active").limit(5).all()
    events = Event.query.filter(Event.name.ilike(like), Event.active == True, Event.status == "active").limit(5).all()
    news_items = News.query.filter(News.title.ilike(like), News.status == "active").limit(5).all()

    from ..models.models import User
    guide_users = User.query.filter(
        (User.first_name.ilike(like) | User.last_name.ilike(like)),
        User.role == "Guide",
    ).limit(5).all()
    guides = [g.guide_profile for g in guide_users if g.guide_profile and g.guide_profile.verification_status == "Approved"]

    results = {
        "attractions": attractions,
        "hotels": hotels,
        "restaurants": restaurants,
        "events": events,
        "guides": guides,
        "news": news_items,
    }
    total = sum(len(v) for v in results.values())
    return render_template("search/results.html", q=q, results=results, total=total)
