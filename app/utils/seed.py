import random
import string
from datetime import datetime, timedelta
from ..extensions import db
from ..models.models import (
    User, Category, Attraction, Guide, Hotel, Restaurant,
    Event, News, Booking, Review, CMSSetting, QRCode,
    FAQ, Partner, Advertisement, Notification
)


def _gen_qr(app, attraction):
    import qrcode
    import os
    qr_dir = os.path.join(app.config["UPLOAD_FOLDER"], "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)
    base_url = "http://localhost:5000"
    url = f"{base_url}/attractions/{attraction.id}"
    qr_img = qrcode.make(url)
    filename = f"qr_{attraction.id}.png"
    path = os.path.join(qr_dir, filename)
    qr_img.save(path)
    return f"/static/uploads/qr_codes/{filename}"


def seed_database():
    from flask import current_app
    db.create_all()

    # Skip if already seeded
    if User.query.filter_by(email="superadmin@edo.gov.ng").first():
        return

    print("🌱 Seeding Edo Odyssey database...")

    # ─────────────── USERS ───────────────
    super_admin = User(
        email="superadmin@edo.gov.ng",
        first_name="Godwin",
        last_name="Obaseki",
        role="Super Admin",
        phone="+234-800-SUPER-ADMIN",
        is_verified=True,
        heritage_points=9999,
        bio="Super Administrator of Edo Odyssey Platform",
        status="active",
    )
    super_admin.set_password("superadmin123")

    admin = User(
        email="admin@edo.gov.ng",
        first_name="ESTA",
        last_name="Administrator",
        role="Agency Admin",
        phone="+234-800-ESTA-ADMIN",
        is_verified=True,
        heritage_points=1000,
        bio="Edo State Tourism Agency Administrator",
        status="active",
    )
    admin.set_password("admin123")

    tourist1 = User(
        email="tourist@gmail.com",
        first_name="Akenzua",
        last_name="Musa",
        role="Tourist",
        phone="+234-801-TOURIST",
        is_verified=True,
        heritage_points=150,
        nationality="Nigerian",
        status="active",
    )
    tourist1.set_password("tourist123")

    tourist2 = User(
        email="jane@visitor.com",
        first_name="Jane",
        last_name="Williams",
        role="Tourist",
        phone="+44-7700-900000",
        is_verified=True,
        heritage_points=320,
        nationality="British",
        status="active",
    )
    tourist2.set_password("tourist123")

    guide_user = User(
        email="guide@edo.gov.ng",
        first_name="Osaro",
        last_name="Edokpayi",
        role="Guide",
        phone="+234-810-GUIDE01",
        is_verified=True,
        status="active",
    )
    guide_user.set_password("guide123")

    guide_user2 = User(
        email="guide2@edo.gov.ng",
        first_name="Itohan",
        last_name="Omoruyi",
        role="Guide",
        phone="+234-810-GUIDE02",
        is_verified=True,
        status="active",
    )
    guide_user2.set_password("guide123")

    hotel_user = User(
        email="hotel@emotan.com",
        first_name="Emotan",
        last_name="Manager",
        role="Hotel",
        phone="+234-820-HOTEL01",
        is_verified=True,
        status="active",
    )
    hotel_user.set_password("hotel123")

    restaurant_user = User(
        email="restaurant@mamaebo.com",
        first_name="Efe",
        last_name="MamaEbo",
        role="Restaurant",
        phone="+234-830-REST001",
        is_verified=True,
        status="active",
    )
    restaurant_user.set_password("mamaebo123")

    db.session.add_all([super_admin, admin, tourist1, tourist2, guide_user, guide_user2, hotel_user, restaurant_user])
    db.session.commit()

    # ─────────────── CATEGORIES ───────────────
    cats = [
        Category(name="History & Museum", description="Historical sites and royal monuments.", type="attraction", icon="bi-building-fill", color="#1a3a6b"),
        Category(name="UNESCO Heritage", description="World-recognized cultural heritage.", type="attraction", icon="bi-globe", color="#c9a227"),
        Category(name="Nature & Wildlife", description="Forests, parks, and ecotourism.", type="attraction", icon="bi-tree-fill", color="#2d8a4e"),
        Category(name="Adventure & Hiking", description="Hills, climbing, outdoor activities.", type="attraction", icon="bi-signpost-fill", color="#e05c27"),
        Category(name="Cultural Festival", description="Traditional festivals and ceremonies.", type="event", icon="bi-music-note-beamed", color="#8a2d8a"),
        Category(name="Sports & Recreation", description="Sports events and recreation.", type="event", icon="bi-trophy-fill", color="#1a7abf"),
    ]
    db.session.add_all(cats)
    db.session.commit()

    # ─────────────── ATTRACTIONS ───────────────
    attractions_data = [
        {
            "name": "The Royal Court of Benin (Oba's Palace)",
            "cat": cats[0], "lat": 6.3450, "lon": 5.6270,
            "description": "Rebuilt in 1915, this magnificent UNESCO-designated court serves as the sacred heart of Edo culture, housing ancient structures and historic court halls. A symbol of the Benin Kingdom's eternal sovereignty.",
            "history": "The Oba's Palace has been the seat of the Benin monarchy for over 600 years. The current structure was rebuilt in 1915 after the British Punitive Expedition of 1897 destroyed much of the original palace.",
            "address": "Oba's Palace Road, Benin City, Edo State",
            "opening_hours": "Mon-Sat 9AM–5PM",
            "ticket_price": 2000,
            "image_url": "https://images.unsplash.com/photo-1580654712603-eb43273aff33?auto=format&fit=crop&q=80&w=800",
            "featured": True,
            "contact": "+234-52-255-000",
            "website": "https://www.edo.gov.ng",
        },
        {
            "name": "Igun Street Bronzecasting Guild",
            "cat": cats[1], "lat": 6.3430, "lon": 5.6240,
            "description": "Walk the ancient alley where master Benin bronze casters have worked for over 600 years. UNESCO-listed as Intangible Cultural Heritage. Watch artisans transform raw metal into masterworks.",
            "history": "The Igun Street bronze casting tradition dates back to the 13th century Benin Kingdom. The guild holds an unbroken lineage of master craftsmen.",
            "address": "Igun Street, Benin City, Edo State",
            "opening_hours": "Daily 8AM–6PM",
            "ticket_price": 500,
            "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=800",
            "featured": True,
            "contact": "+234-52-256-111",
        },
        {
            "name": "Okomu National Park",
            "cat": cats[2], "lat": 6.2800, "lon": 5.4500,
            "description": "One of the last surviving lowland tropical rainforests in Nigeria. Home to forest elephants, chimpanzees, white-throated monkeys, and hundreds of rare bird species.",
            "history": "Gazetted in 1935, Okomu was upgraded to full National Park status in 1999. It protects one of the most biodiverse ecosystems in West Africa.",
            "address": "Ovia South-West LGA, Edo State",
            "opening_hours": "Daily 7AM–5PM",
            "ticket_price": 3000,
            "image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&q=80&w=800",
            "featured": True,
            "contact": "+234-52-260-200",
        },
        {
            "name": "Ancient Benin Moats (Iya)",
            "cat": cats[1], "lat": 6.3380, "lon": 5.6120,
            "description": "The largest man-made earthworks in the world. Built over 1,000 years ago, these earthen walls and moats once enclosed the city of Benin—a feat of engineering that dwarfs the Great Wall of China in total length.",
            "history": "Built progressively from the 13th to 15th centuries, the Benin Moats (Iya) are recognized by the Guinness World Records as the largest man-made earthworks.",
            "address": "Ring Road, Benin City, Edo State",
            "opening_hours": "Always Open",
            "ticket_price": 0,
            "image_url": "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&q=80&w=800",
            "featured": False,
        },
        {
            "name": "Osun Sacred Grove (Iguae-Okun)",
            "cat": cats[0], "lat": 6.3500, "lon": 5.6300,
            "description": "A sacred forest sanctuary dedicated to ancestral spirits and deities. Ancient shrines, towering trees, and ceremonial sites make this a deeply spiritual cultural landscape.",
            "history": "The grove has served as a place of worship, community gathering, and spiritual consultation for the Edo people for centuries.",
            "address": "GRA, Benin City, Edo State",
            "opening_hours": "Tue-Sun 8AM–4PM",
            "ticket_price": 1000,
            "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&q=80&w=800",
            "featured": False,
        },
        {
            "name": "Eki Market (Ring Road)",
            "cat": cats[0], "lat": 6.3400, "lon": 5.6220,
            "description": "Benin City's oldest and most vibrant open-air market. A cultural landmark where traditional textiles, bronze artifacts, native medicines, and local produce have been traded for centuries.",
            "history": "Eki Market has functioned as the commercial and social heart of Benin City since the height of the Benin Kingdom.",
            "address": "Ring Road, Benin City, Edo State",
            "opening_hours": "Daily 6AM–8PM",
            "ticket_price": 0,
            "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&q=80&w=800",
            "featured": False,
        },
    ]

    attraction_objs = []
    for d in attractions_data:
        a = Attraction(
            name=d["name"],
            category_id=d["cat"].id,
            description=d["description"],
            address=d["address"],
            history=d.get("history", ""),
            opening_hours=d.get("opening_hours", ""),
            ticket_price=d.get("ticket_price", 0),
            image_url=d.get("image_url", ""),
            latitude=d["lat"],
            longitude=d["lon"],
            contact=d.get("contact", ""),
            website=d.get("website", ""),
            featured=d.get("featured", False),
            active=True,
            status="active",
        )
        db.session.add(a)
        attraction_objs.append(a)
    db.session.commit()

    # Generate QR codes
    for att in attraction_objs:
        try:
            path = _gen_qr(current_app, att)
            qr = QRCode(attraction_id=att.id, qr_image_path=path, status="active")
            db.session.add(qr)
        except Exception:
            pass
    db.session.commit()

    # ─────────────── GUIDES ───────────────
    g1 = Guide(
        user_id=guide_user.id,
        bio="Licensed Edo State Tour Guide specializing in Royal History, Igun Street Bronze guild, and the Oba's Palace. Over 8 years guiding international tourists.",
        languages="English, Edo, Pidgin, Yoruba",
        experience=8,
        hourly_rate=2500.0,
        daily_rate=15000.0,
        availability="Available",
        verification_status="Approved",
        specializations="Royal History, Bronze Art, Heritage Sites",
        license_number="ESTA-G-2018-001",
        status="active",
    )
    g2 = Guide(
        user_id=guide_user2.id,
        bio="Expert eco-tourism guide for Okomu National Park and Edo's rainforest regions. Certified wildlife tracker and birding specialist.",
        languages="English, Edo, French",
        experience=5,
        hourly_rate=2000.0,
        daily_rate=12000.0,
        availability="Available",
        verification_status="Approved",
        specializations="Eco-tourism, Wildlife, Bird Watching",
        license_number="ESTA-G-2021-004",
        status="active",
    )
    db.session.add_all([g1, g2])
    db.session.commit()

    # ─────────────── HOTELS ───────────────
    hotels_data = [
        {
            "name": "Emotan Hotel & Suites",
            "address": "3 Sapele Road, GRA, Benin City, Edo State",
            "description": "A premium 4-star hotel in the heart of Benin City's Government Reserved Area. Features exquisite Edo cultural décor, a rooftop bar with panoramic views, Olympic-standard pool, and world-class conference facilities.",
            "facilities": "Swimming Pool, WiFi, Gym, Restaurant, Bar, Conference Hall, Spa, Parking",
            "price_per_night": 35000.0, "stars": 4,
            "lat": 6.3490, "lon": 5.6280,
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80&w=800",
            "contact": "+234-52-257-800", "website": "https://emotanhotel.com",
            "featured": True, "total_rooms": 85,
        },
        {
            "name": "Royal Heritage Lodge",
            "address": "15 Airport Road, Benin City, Edo State",
            "description": "A boutique heritage lodge inspired by traditional Benin architecture. Each room is decorated with authentic local art and hand-crafted bronze fixtures. Located minutes from the international airport.",
            "facilities": "WiFi, Restaurant, Bar, Garden, Parking, Room Service",
            "price_per_night": 22000.0, "stars": 3,
            "lat": 6.3200, "lon": 5.5900,
            "image_url": "https://images.unsplash.com/photo-1455587734955-081b22074882?auto=format&fit=crop&q=80&w=800",
            "contact": "+234-52-258-900", "featured": False, "total_rooms": 42,
        },
        {
            "name": "Okomu Forest Resort",
            "address": "Okomu National Park Access Road, Ovia South-West, Edo State",
            "description": "Immersive eco-resort on the edge of Okomu National Park. Luxury chalets nestled in the forest, guided dawn safaris, night nature walks, and an outdoor dining terrace overlooking the canopy.",
            "facilities": "WiFi, Restaurant, Safari Tours, Nature Walks, Bar, Bonfire Area",
            "price_per_night": 45000.0, "stars": 4,
            "lat": 6.2700, "lon": 5.4400,
            "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&q=80&w=800",
            "contact": "+234-52-260-500", "featured": True, "total_rooms": 30,
        },
    ]
    for d in hotels_data:
        h = Hotel(
            name=d["name"], address=d["address"], description=d["description"],
            facilities=d["facilities"], price_per_night=d["price_per_night"],
            image_url=d["image_url"], latitude=d["lat"], longitude=d["lon"],
            contact=d.get("contact", ""), website=d.get("website", ""),
            stars=d["stars"], total_rooms=d["total_rooms"],
            featured=d["featured"], status="active",
        )
        db.session.add(h)
    db.session.commit()

    # ─────────────── RESTAURANTS ───────────────
    restaurants_data = [
        {
            "name": "Mama Ebo's Kitchen",
            "address": "22 Akenzua Street, Benin City, Edo State",
            "description": "An authentic Edo cuisine restaurant serving traditional Benin soups including banga soup, egusi, ofe akwu, and fresh fish pepper soup. Family recipes passed down for four generations.",
            "cuisine": "Traditional Edo, Nigerian",
            "opening_hours": "Daily 8AM–10PM",
            "lat": 6.3420, "lon": 5.6250,
            "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&q=80&w=800",
            "contact": "+234-803-EBO-MAMA",
            "price_range": "₦₦", "featured": True,
        },
        {
            "name": "The Benin Grill",
            "address": "5 Reservation Road, GRA, Benin City",
            "description": "An upscale grill restaurant blending Edo flavors with continental cuisine. Signature dish: Suya-glazed river fish with ukodo served on banana leaf. Live jazz Thursday-Saturday.",
            "cuisine": "Fusion, Continental, Nigerian",
            "opening_hours": "Tue-Sun 12PM–11PM",
            "lat": 6.3470, "lon": 5.6270,
            "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&q=80&w=800",
            "contact": "+234-52-257-600",
            "price_range": "₦₦₦", "featured": True,
        },
        {
            "name": "Igun Café & Lounge",
            "address": "Igun Street, Benin City, Edo State",
            "description": "A cultural café set in a restored colonial building on historic Igun Street. Serves light meals, fresh juices, palm wine, and locally roasted coffee alongside a gallery of bronze art.",
            "cuisine": "Café, Light Meals, Local",
            "opening_hours": "Mon-Sat 7AM–8PM",
            "lat": 6.3435, "lon": 5.6245,
            "image_url": "https://images.unsplash.com/photo-1521017432531-fbd92d768814?auto=format&fit=crop&q=80&w=800",
            "contact": "+234-803-IGUN-CAFE",
            "price_range": "₦", "featured": False,
        },
    ]
    for d in restaurants_data:
        r = Restaurant(
            name=d["name"], address=d["address"], description=d["description"],
            cuisine=d["cuisine"], opening_hours=d["opening_hours"],
            image_url=d["image_url"], latitude=d["lat"], longitude=d["lon"],
            contact=d.get("contact", ""), price_range=d["price_range"],
            featured=d["featured"], status="active",
        )
        db.session.add(r)
    db.session.commit()

    # ─────────────── EVENTS ───────────────
    events_data = [
        {
            "name": "Igue Festival 2026",
            "description": "The grand annual celebration of the Oba of Benin. The Igue festival is a royal thanksgiving—a week of ancient ceremonies, cultural processions, masquerades, traditional music, and royal feasts. One of West Africa's most spectacular living cultural events.",
            "date": datetime(2026, 12, 20, 9, 0),
            "end_date": datetime(2026, 12, 27, 21, 0),
            "location": "Oba's Palace, Benin City",
            "image_url": "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?auto=format&fit=crop&q=80&w=800",
            "ticket_price": 0, "capacity": 10000, "featured": True,
            "category": "Cultural Festival",
            "organizer": "Edo State Tourism Agency",
            "lat": 6.345, "lon": 5.627,
        },
        {
            "name": "Okomu Eco-Safari Weekend",
            "description": "A guided weekend eco-safari through Okomu National Park. Includes dawn game drives, forest walks, bird watching, wildlife photography workshops, and a bonfire dinner under the stars.",
            "date": datetime(2026, 8, 15, 6, 0),
            "end_date": datetime(2026, 8, 17, 18, 0),
            "location": "Okomu National Park",
            "image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&q=80&w=800",
            "ticket_price": 15000, "capacity": 50, "featured": True,
            "category": "Eco-tourism",
            "organizer": "ESTA & Okomu National Park Authority",
            "lat": 6.28, "lon": 5.45,
        },
        {
            "name": "Benin Bronze Art Fair",
            "description": "A 3-day international art fair showcasing traditional and contemporary Benin bronze sculpture, enamel work, and ivory carvings. Collectors, curators, and tourists from across the globe attend.",
            "date": datetime(2026, 10, 5, 10, 0),
            "end_date": datetime(2026, 10, 7, 18, 0),
            "location": "Ring Road Exhibition Centre, Benin City",
            "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=800",
            "ticket_price": 5000, "capacity": 500, "featured": False,
            "category": "Art & Culture",
            "organizer": "Igun Street Bronze Guild",
            "lat": 6.341, "lon": 5.623,
        },
    ]
    for d in events_data:
        e = Event(
            name=d["name"], description=d["description"],
            date=d["date"], end_date=d.get("end_date"),
            location=d["location"], image_url=d["image_url"],
            ticket_price=d["ticket_price"], capacity=d["capacity"],
            featured=d["featured"], category=d.get("category"),
            organizer=d.get("organizer"), active=True, status="active",
            latitude=d.get("lat"), longitude=d.get("lon"),
        )
        db.session.add(e)
    db.session.commit()

    # ─────────────── NEWS ───────────────
    news_data = [
        {
            "title": "Edo State Partners with UNESCO to Restore Historic Benin Moats",
            "content": "The Edo State Tourism Agency (ESTA) has launched a multi-billion Naira conservation partnership with UNESCO to dredge and restore the ancient Benin Moats—the world's largest man-made earthworks. The restoration project, spanning 16,000 km² of earthen walls, will create an outdoor heritage trail accessible to tourists from around the world. Governor Obaseki signed the agreement at a ceremony attended by the UNESCO Director-General and international heritage experts.",
            "category": "Government", "tags": "Moats, Conservation, UNESCO, Heritage",
            "image_url": "https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?auto=format&fit=crop&q=80&w=800",
            "featured": True, "author": "ESTA Communications",
        },
        {
            "title": "Igun Street Celebrates Historic Return of Benin Bronzes",
            "content": "Local artisans and bronze guilds on the historic Igun Street celebrated the repatriation of eight Benin Bronzes from European museums. The returned masterworks—looted during the British Punitive Expedition of 1897—will go on public display at the new Royal Museum before finding their permanent home at the Oba's Palace Pavilion. The celebrations included traditional ceremonies, live demonstrations by master bronze casters, and a market fair drawing thousands of visitors.",
            "category": "Culture", "tags": "Bronzes, Repatriation, Igun Street, Royal Court",
            "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=800",
            "featured": True, "author": "Dr. Iyare Obiora",
        },
        {
            "title": "ESTA Launches New Digital QR Heritage Trail Through Benin City",
            "content": "Tourists can now explore Benin City's historic sites through an interactive digital trail powered by QR codes installed at 24 heritage locations. Scanning each QR code with a smartphone opens rich multimedia content—history, audio narration, photo galleries, and nearby attraction recommendations—on the Edo Odyssey platform. The trail was developed by ESTA in partnership with the Ministry of Digital Economy.",
            "category": "Technology", "tags": "QR Code, Digital, Heritage, Tourism",
            "image_url": "https://images.unsplash.com/photo-1580654712603-eb43273aff33?auto=format&fit=crop&q=80&w=800",
            "featured": False, "author": "ESTA Tech Team",
        },
        {
            "title": "Okomu National Park Records Record Visitor Numbers in 2026",
            "content": "Okomu National Park welcomed over 12,000 visitors in the first half of 2026—a 340% increase from the same period in 2023. Park rangers attribute the surge to the Edo Odyssey platform's targeted marketing, the introduction of eco-safari weekend packages, and new chimpanzee tracking programs. The park has applied for IUCN Category II status, which would make it eligible for international conservation funding.",
            "category": "Conservation", "tags": "Okomu, Wildlife, Eco-tourism, Conservation",
            "image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&q=80&w=800",
            "featured": False, "author": "Ranger Joseph Ehigie",
        },
    ]
    for d in news_data:
        from ..utils.helpers import slugify
        n = News(
            title=d["title"], content=d["content"],
            category=d["category"], tags=d["tags"],
            image_url=d["image_url"], featured=d["featured"],
            author=d["author"], status="active",
            slug=slugify(d["title"]) + "-" + "".join(random.choices("0123456789", k=4)),
        )
        db.session.add(n)
    db.session.commit()

    # ─────────────── BOOKINGS & REVIEWS ───────────────
    hotel1 = Hotel.query.first()
    guide1 = Guide.query.first()
    attr1 = Attraction.query.first()
    attr2 = Attraction.query.offset(1).first()

    b1 = Booking(
        user_id=tourist1.id, booking_type="Hotel", target_id=hotel1.id if hotel1 else 1,
        target_name="Emotan Hotel & Suites",
        start_date=datetime(2026, 9, 15), end_date=datetime(2026, 9, 18),
        total_price=105000, booking_status="Confirmed",
        reference_code="EO" + "A3B5C7D9", num_guests=2, status="active",
    )
    b2 = Booking(
        user_id=tourist1.id, booking_type="Guide", target_id=guide1.id if guide1 else 1,
        target_name="Osaro Edokpayi",
        start_date=datetime(2026, 9, 16), end_date=datetime(2026, 9, 16),
        total_price=7500, booking_status="Completed",
        reference_code="EO" + "E2F4G6H8", num_guests=1, status="active",
    )
    b3 = Booking(
        user_id=tourist2.id, booking_type="Hotel", target_id=hotel1.id if hotel1 else 1,
        target_name="Emotan Hotel & Suites",
        start_date=datetime(2026, 10, 5), end_date=datetime(2026, 10, 8),
        total_price=140000, booking_status="Pending",
        reference_code="EO" + "I0J2K4L6", num_guests=3, status="active",
    )
    db.session.add_all([b1, b2, b3])
    db.session.commit()

    # Reviews
    reviews = [
        Review(user_id=tourist1.id, target_type="Attraction", target_id=attr1.id if attr1 else 1, rating=5, comment="An awe-inspiring experience. The palace grounds are sacred and breathtaking. Our guide Osaro explained every detail beautifully.", is_approved=True, status="active"),
        Review(user_id=tourist2.id, target_type="Attraction", target_id=attr1.id if attr1 else 1, rating=5, comment="Absolutely unmissable. The history, the architecture, the spiritual atmosphere—nothing quite prepares you for it. Visit before the restoration.", is_approved=True, status="active"),
        Review(user_id=tourist1.id, target_type="Guide", target_id=guide1.id if guide1 else 1, rating=5, comment="Osaro is phenomenal—knowledgeable, passionate, and genuinely invested in sharing Edo culture. Booked him for three days and wish it was three weeks.", is_approved=True, status="active"),
        Review(user_id=tourist2.id, target_type="Hotel", target_id=hotel1.id if hotel1 else 1, rating=4, comment="Excellent hotel with beautiful Benin-inspired décor. Room was spotless, staff incredibly welcoming. The rooftop bar at sunset is perfection.", is_approved=True, status="active"),
        Review(user_id=tourist1.id, target_type="Attraction", target_id=attr2.id if attr2 else 1, rating=5, comment="Watching the bronze casters work is mesmerizing. 600 years of unbroken tradition on one street. Bought a stunning casting for my living room.", is_approved=True, status="active"),
    ]
    db.session.add_all(reviews)

    # ─────────────── CMS SETTINGS ───────────────
    cms_data = [
        ("hero_title", "Edo State – Cradle of Black Civilization", "Hero Title", "homepage"),
        ("hero_subtitle", "Welcome to the official digital gateway of the Edo State Tourism Agency (ESTA). Explore ancient royal palaces, watch world-famous bronze casters at work, track wildlife in tropical rainforests, and book certified local tour guides—all in one place.", "Hero Subtitle", "homepage"),
        ("hero_image", "https://images.unsplash.com/photo-1580654712603-eb43273aff33?auto=format&fit=crop&q=80&w=1600", "Hero Image URL", "homepage"),
        ("about_agency", "The Edo State Tourism Agency (ESTA) is a statutory public corporation established to guide, preserve, license, and promote the natural landmarks, cultural festivals, and historical heritage monuments of the Edo Kingdom. We secure traveler logs, train professional tour guides, and maintain digital GIS databases for world-class tourism.", "About Agency", "about"),
        ("agency_vision", "To make Edo State the foremost cultural and eco-tourism destination in West Africa by 2030.", "Agency Vision", "about"),
        ("agency_mission", "To digitize, preserve, and promote Edo's cultural heritage while creating sustainable tourism experiences that empower local communities and celebrate Edo civilization.", "Agency Mission", "about"),
        ("contact_email", "info@esta.edo.gov.ng", "Contact Email", "contact"),
        ("contact_phone", "+234 (0) 52 255 000", "Contact Phone", "contact"),
        ("contact_address", "ESTA Headquarters, Government House Road, GRA, Benin City, Edo State, Nigeria", "Contact Address", "contact"),
        ("privacy_policy", "ESTA processes tourist logs, scan history, and reservations in full compliance with the Nigeria Data Protection Regulation (NDPR) to secure personal identifiers against breaches. We never sell your data to third parties.", "Privacy Policy", "legal"),
        ("terms_conditions", "By reserving tour guides, hotels, or scanning monument QR plaques, users agree to respect local customs, maintain clean environment guidelines in reserves, and abide by royal court security protocols.", "Terms & Conditions", "legal"),
        ("footer_text", "© 2026 Edo State Tourism Agency (ESTA). All rights reserved.", "Footer Text", "general"),
        ("google_maps_key", "YOUR_GOOGLE_MAPS_API_KEY", "Google Maps API Key", "integrations"),
        ("meta_description", "Explore Edo State's world-class cultural heritage, wildlife, and tourism experiences through the official Edo Odyssey digital platform.", "Meta Description", "seo"),
    ]
    for key, value, label, group in cms_data:
        s = CMSSetting(key=key, value=value, label=label, group=group)
        db.session.add(s)

    # ─────────────── FAQS ───────────────
    faqs = [
        FAQ(question="Do I need a special permit to visit the Oba's Palace?", answer="Yes, while tourists can photograph the outer palace walls and visit the administrative court, entering the sacred inner chambers requires prior administrative clearance or booking a certified royal tour guide via this platform.", order=1),
        FAQ(question="Are there direct shuttles to Okomu National Park?", answer="ESTA operates a bi-weekly weekend eco-safari shuttle from Benin City directly to Okomu. You can register for the next shuttle under the 'Events' tab on our homepage.", order=2),
        FAQ(question="How do I become a certified tour guide on Edo Odyssey?", answer="Register on the platform with the 'Guide' role, submit your ID, certifications, and experience record. ESTA will review your application within 5 business days and may schedule an in-person assessment.", order=3),
        FAQ(question="Can I pay for bookings in foreign currency?", answer="Currently all payments are processed in Nigerian Naira (NGN). International tourists can pay by card through our secure payment gateway, which automatically handles currency conversion.", order=4),
        FAQ(question="Is the Igun Street bronze casting area safe to visit alone?", answer="Yes, Igun Street is a safe and welcoming heritage district open daily. We recommend a certified guide for the full cultural experience and to access private studios.", order=5),
    ]
    db.session.add_all(faqs)

    # ─────────────── PARTNERS ───────────────
    partners = [
        Partner(name="UNESCO", logo_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/UNESCO_logo.svg/200px-UNESCO_logo.svg.png", type="partner", active=True),
        Partner(name="Nigerian Tourism Development Corporation", logo_url="https://placehold.co/200x80/1a3a6b/c9a227?text=NTDC", type="partner", active=True),
        Partner(name="Edo State Government", logo_url="https://placehold.co/200x80/1a3a6b/ffffff?text=Edo+Gov", type="sponsor", active=True),
        Partner(name="First Bank Nigeria", logo_url="https://placehold.co/200x80/0a2e5c/ffffff?text=First+Bank", type="sponsor", active=True),
    ]
    db.session.add_all(partners)

    # ─────────────── NOTIFICATIONS ───────────────
    notifs = [
        Notification(user_id=tourist1.id, title="Welcome to Edo Odyssey!", message="Your account has been verified. Start exploring Edo State's incredible heritage.", type="success"),
        Notification(user_id=tourist1.id, title="Booking Confirmed", message="Your booking at Emotan Hotel & Suites (Sep 15–18) has been confirmed. Reference: EOA3B5C7D9.", type="success", link="/dashboard"),
        Notification(user_id=tourist2.id, title="Welcome to Edo Odyssey!", message="Your account has been verified. Start exploring and discovering Edo culture.", type="success"),
        Notification(user_id=guide_user.id, title="New Booking Request", message="Tourist Akenzua Musa has requested a guided tour. Please review and confirm.", type="info", link="/dashboard"),
    ]
    db.session.add_all(notifs)

    db.session.commit()
    print("✅ Database seeded successfully!")
    print("\n🔑 QUICK ACCESS LOGINS:")
    print("   Super Admin → superadmin@edo.gov.ng / superadmin123")
    print("   Admin       → admin@edo.gov.ng / admin123")
    print("   Tourist     → tourist@gmail.com / tourist123")
    print("   Tourist 2   → jane@visitor.com / tourist123")
    print("   Guide       → guide@edo.gov.ng / guide123")
    print("   Hotel       → hotel@emotan.com / hotel123")
    print("   Restaurant  → restaurant@mamaebo.com / mamaebo123")
