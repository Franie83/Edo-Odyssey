import uuid
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


def gen_uuid():
    return str(uuid.uuid4())


class BaseModel(db.Model):
    """Abstract base with audit fields."""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=gen_uuid, unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default="active", nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        self.status = "deleted"

    @property
    def is_deleted(self):
        return self.deleted_at is not None


class User(UserMixin, BaseModel):
    __tablename__ = "users"

    email = db.Column(db.String(150), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default="Tourist", nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    heritage_points = db.Column(db.Integer, default=0, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    nationality = db.Column(db.String(100), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    bookings = db.relationship("Booking", back_populates="user", lazy="dynamic")
    reviews = db.relationship("Review", back_populates="user", lazy="dynamic")
    guide_profile = db.relationship("Guide", back_populates="user", uselist=False)
    notifications = db.relationship("Notification", back_populates="user", lazy="dynamic")
    favourites = db.relationship("Favourite", back_populates="user", lazy="dynamic")
    payments = db.relationship("Payment", back_populates="user", lazy="dynamic")
    audit_logs = db.relationship("AuditLog", foreign_keys="AuditLog.user_id", back_populates="user", lazy="dynamic")
    
    # New relationships for owned entities
    owned_attractions = db.relationship("Attraction", back_populates="owner", foreign_keys="Attraction.user_id", lazy="dynamic")
    owned_hotels = db.relationship("Hotel", back_populates="owner", foreign_keys="Hotel.user_id", lazy="dynamic")
    owned_restaurants = db.relationship("Restaurant", back_populates="owner", foreign_keys="Restaurant.user_id", lazy="dynamic")
    owned_events = db.relationship("Event", back_populates="owner", foreign_keys="Event.user_id", lazy="dynamic")  # Add this

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role in ("Agency Admin", "Super Admin")

    @property
    def is_super_admin(self):
        return self.role == "Super Admin"

    def __repr__(self):
        return f"<User {self.email}>"


class Category(BaseModel):
    __tablename__ = "categories"

    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50), default="bi-tag", nullable=True)
    color = db.Column(db.String(20), default="#1a3a6b", nullable=True)

    attractions = db.relationship("Attraction", back_populates="category", lazy="dynamic")


class Attraction(BaseModel):
    __tablename__ = "attractions"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Owner/Manager
    name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    description = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    history = db.Column(db.Text, nullable=True)
    opening_hours = db.Column(db.String(100), nullable=True)
    ticket_price = db.Column(db.Float, default=0.0, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    gallery_urls = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    views = db.Column(db.Integer, default=0, nullable=False)
    visit_count = db.Column(db.Integer, default=0, nullable=False)

    category = db.relationship("Category", back_populates="attractions")
    qr_codes = db.relationship("QRCode", back_populates="attraction", cascade="all, delete-orphan")
    reviews = db.relationship("Review", primaryjoin="and_(Review.target_type=='Attraction', Review.target_id==Attraction.id)", foreign_keys="Review.target_id", lazy="dynamic", overlaps="reviews")
    favourites = db.relationship("Favourite", primaryjoin="and_(Favourite.target_type=='Attraction', Favourite.target_id==Attraction.id)", foreign_keys="Favourite.target_id", lazy="dynamic", overlaps="favourites")
    owner = db.relationship("User", back_populates="owned_attractions", foreign_keys=[user_id])

    @property
    def avg_rating(self):
        reviews = Review.query.filter_by(target_type="Attraction", target_id=self.id).all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def gallery_list(self):
        if self.gallery_urls:
            return [u.strip() for u in self.gallery_urls.split(",") if u.strip()]
        return []


class Guide(BaseModel):
    __tablename__ = "guides"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    languages = db.Column(db.String(255), nullable=True)
    experience = db.Column(db.Integer, default=0, nullable=False)
    hourly_rate = db.Column(db.Float, default=0.0, nullable=False)
    daily_rate = db.Column(db.Float, default=0.0, nullable=False)
    availability = db.Column(db.String(255), default="Available", nullable=False)
    verification_status = db.Column(db.String(50), default="Pending", nullable=False)
    specializations = db.Column(db.String(255), nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    total_tours = db.Column(db.Integer, default=0, nullable=False)
    photo_url = db.Column(db.String(255), nullable=True)
    license_number = db.Column(db.String(100), nullable=True)

    user = db.relationship("User", back_populates="guide_profile")
    availabilities = db.relationship("GuideAvailability", back_populates="guide", cascade="all, delete-orphan")

    @property
    def avg_rating(self):
        reviews = Review.query.filter_by(target_type="Guide", target_id=self.id).all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def languages_list(self):
        if self.languages:
            return [l.strip() for l in self.languages.split(",")]
        return []


class GuideAvailability(db.Model):
    __tablename__ = "guide_availabilities"
    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(db.Integer, db.ForeignKey("guides.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    note = db.Column(db.String(255), nullable=True)
    guide = db.relationship("Guide", back_populates="availabilities")


class Hotel(BaseModel):
    __tablename__ = "hotels"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Hotel Manager
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    facilities = db.Column(db.Text, nullable=True)
    price_per_night = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    gallery_urls = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    stars = db.Column(db.Integer, default=3, nullable=False)
    total_rooms = db.Column(db.Integer, default=0, nullable=False)
    check_in_time = db.Column(db.String(20), default="14:00", nullable=True)
    check_out_time = db.Column(db.String(20), default="12:00", nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)

    rooms = db.relationship("HotelRoom", back_populates="hotel", cascade="all, delete-orphan")
    owner = db.relationship("User", back_populates="owned_hotels", foreign_keys=[user_id])

    @property
    def avg_rating(self):
        reviews = Review.query.filter_by(target_type="Hotel", target_id=self.id).all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def facilities_list(self):
        if self.facilities:
            return [f.strip() for f in self.facilities.split(",")]
        return []


class HotelRoom(db.Model):
    __tablename__ = "hotel_rooms"
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey("hotels.id"), nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, default=2)
    amenities = db.Column(db.Text, nullable=True)
    available = db.Column(db.Boolean, default=True)
    hotel = db.relationship("Hotel", back_populates="rooms")


class Restaurant(BaseModel):
    __tablename__ = "restaurants"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Restaurant Owner
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cuisine = db.Column(db.String(100), nullable=False)
    opening_hours = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    gallery_urls = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    price_range = db.Column(db.String(20), default="$$", nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    reservation_available = db.Column(db.Boolean, default=True, nullable=False)

    menus = db.relationship("RestaurantMenu", back_populates="restaurant", cascade="all, delete-orphan")
    owner = db.relationship("User", back_populates="owned_restaurants", foreign_keys=[user_id])

    @property
    def avg_rating(self):
        reviews = Review.query.filter_by(target_type="Restaurant", target_id=self.id).all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)


class RestaurantMenu(db.Model):
    __tablename__ = "restaurant_menus"
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    item_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    available = db.Column(db.Boolean, default=True)
    restaurant = db.relationship("Restaurant", back_populates="menus")


class Event(BaseModel):
    __tablename__ = "events"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Event Organizer
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    gallery_urls = db.Column(db.Text, nullable=True)
    ticket_price = db.Column(db.Float, default=0.0, nullable=False)
    capacity = db.Column(db.Integer, default=0, nullable=False)
    organizer = db.Column(db.String(150), nullable=True)
    contact = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(100), nullable=True)

    # Relationship
    owner = db.relationship("User", back_populates="owned_events", foreign_keys=[user_id])

    @property
    def is_upcoming(self):
        return self.date > datetime.utcnow()

    @property
    def days_until(self):
        delta = self.date - datetime.utcnow()
        return max(0, delta.days)


class News(BaseModel):
    __tablename__ = "news"

    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    author = db.Column(db.String(150), nullable=True)
    views = db.Column(db.Integer, default=0, nullable=False)

    comments = db.relationship("NewsComment", back_populates="news_article", cascade="all, delete-orphan")

    @property
    def tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(",")]
        return []


class NewsComment(db.Model):
    __tablename__ = "news_comments"
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey("news.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    news_article = db.relationship("News", back_populates="comments")
    user = db.relationship("User")


class Booking(BaseModel):
    __tablename__ = "bookings"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    booking_type = db.Column(db.String(50), nullable=False)  # Guide, Hotel, Tour, Event
    target_id = db.Column(db.Integer, nullable=False)
    target_name = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    booking_status = db.Column(db.String(50), default="Pending", nullable=False)  # Pending, Approved, Completed, Cancelled
    cancellation_reason = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    reference_code = db.Column(db.String(20), nullable=True, unique=True)
    num_guests = db.Column(db.Integer, default=1, nullable=False)

    user = db.relationship("User", back_populates="bookings")
    payment = db.relationship("Payment", back_populates="booking", uselist=False)


class Review(BaseModel):
    __tablename__ = "reviews"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)  # Hotel, Guide, Restaurant, Attraction
    target_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    helpful_count = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship("User", back_populates="reviews")
    
    # Polymorphic relationships for easy access to the target
    @property
    def target(self):
        """Get the target object (Attraction, Guide, Hotel, or Restaurant)"""
        if self.target_type == 'Attraction':
            return Attraction.query.get(self.target_id)
        elif self.target_type == 'Guide':
            return Guide.query.get(self.target_id)
        elif self.target_type == 'Hotel':
            return Hotel.query.get(self.target_id)
        elif self.target_type == 'Restaurant':
            return Restaurant.query.get(self.target_id)
        elif self.target_type == 'Event':
            return Event.query.get(self.target_id)
        return None
    
    @property
    def target_name(self):
        """Get the display name of the target"""
        target = self.target
        if target:
            if hasattr(target, 'name'):
                return target.name
            elif hasattr(target, 'full_name'):
                return target.full_name
            elif hasattr(target, 'user') and hasattr(target.user, 'full_name'):
                return target.user.full_name
        return f"{self.target_type} #{self.target_id}"


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    operator_email = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(500), nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    module = db.Column(db.String(100), nullable=True)
    record_id = db.Column(db.Integer, nullable=True)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="audit_logs")


class QRCode(db.Model):
    __tablename__ = 'qr_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'))
    code = db.Column(db.String(255))
    qr_image_path = db.Column(db.String(500))
    url = db.Column(db.String(500))
    scanned_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attraction = db.relationship('Attraction', backref='qr_code_record')


class CMSSetting(db.Model):
    __tablename__ = "cms_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    label = db.Column(db.String(150), nullable=True)
    group = db.Column(db.String(50), default="general", nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default="info", nullable=False)  # info, success, warning, danger
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(255), nullable=True)

    user = db.relationship("User", back_populates="notifications")


class FAQ(db.Model):
    __tablename__ = "faqs"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default="general", nullable=True)
    order = db.Column(db.Integer, default=0, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Partner(db.Model):
    __tablename__ = "partners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), default="partner", nullable=False)  # partner, sponsor
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Advertisement(db.Model):
    __tablename__ = "advertisements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    link = db.Column(db.String(255), nullable=True)
    position = db.Column(db.String(50), default="sidebar", nullable=False)
    active = db.Column(db.Boolean, default=True)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)


class Favourite(db.Model):
    __tablename__ = "favourites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="favourites")


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=gen_uuid, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="NGN", nullable=False)
    payment_method = db.Column(db.String(50), nullable=True)
    payment_status = db.Column(db.String(50), default="Pending", nullable=False)
    reference = db.Column(db.String(100), nullable=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="payments")
    booking = db.relationship("Booking", back_populates="payment")