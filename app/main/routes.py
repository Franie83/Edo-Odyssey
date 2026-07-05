from flask import Blueprint, render_template, abort
from ..models.models import Attraction, Hotel, Restaurant, Event, News, Guide, Category, Partner, FAQ

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    featured_attractions = Attraction.query.filter_by(featured=True, active=True, status="active").limit(6).all()
    featured_hotels = Hotel.query.filter_by(featured=True, status="active").limit(3).all()
    featured_restaurants = Restaurant.query.filter_by(featured=True, status="active").limit(3).all()
    upcoming_events = Event.query.filter_by(featured=True, active=True, status="active").limit(3).all()
    recent_news = News.query.filter_by(status="active").order_by(News.created_at.desc()).limit(4).all()
    
    # 🎯 SHOW ALL APPROVED GUIDES
    featured_guides = Guide.query.filter_by(
        verification_status="Approved", 
        status="active"
    ).all()
    
    # 🐛 DEBUG: Print to console to verify
    print("\n" + "="*50)
    print("🏠 HOMEPAGE DATA:")
    print("="*50)
    print(f"📋 Total guides: {len(featured_guides)}")
    for g in featured_guides:
        print(f"  - {g.user.full_name if g.user else 'Unknown'}")
    
    print(f"\n🏛️ Featured Attractions: {len(featured_attractions)}")
    for att in featured_attractions:
        print(f"  - {att.name}")
    
    print(f"\n🏨 Featured Hotels: {len(featured_hotels)}")
    for hotel in featured_hotels:
        print(f"  - {hotel.name}")
    
    print(f"\n🎪 Featured Events: {len(upcoming_events)}")
    for event in upcoming_events:
        print(f"  - {event.name}")
    
    print(f"\n📰 Recent News: {len(recent_news)}")
    for news in recent_news:
        print(f"  - {news.title}")
    print("="*50 + "\n")
    
    partners = Partner.query.filter_by(active=True).all()
    categories = Category.query.filter_by(type="attraction", status="active").all()
    total_attractions = Attraction.query.filter_by(status="active").count()
    total_guides = Guide.query.filter_by(verification_status="Approved", status="active").count()
    total_hotels = Hotel.query.filter_by(status="active").count()
    
    return render_template(
        "main/home.html",
        featured_attractions=featured_attractions,
        featured_hotels=featured_hotels,
        featured_restaurants=featured_restaurants,
        upcoming_events=upcoming_events,
        recent_news=recent_news,
        featured_guides=featured_guides,
        partners=partners,
        categories=categories,
        total_attractions=total_attractions,
        total_guides=total_guides,
        total_hotels=total_hotels,
    )


@main_bp.route("/about")
def about():
    return render_template("main/about.html")


@main_bp.route("/contact")
def contact():
    return render_template("main/contact.html")


@main_bp.route("/privacy")
def privacy():
    return render_template("main/privacy.html")


@main_bp.route("/terms")
def terms():
    return render_template("main/terms.html")


@main_bp.route("/faq")
def faq():
    faqs = FAQ.query.filter_by(active=True).order_by(FAQ.order).all()
    return render_template("main/faq.html", faqs=faqs)