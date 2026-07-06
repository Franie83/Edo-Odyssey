from app import create_app
from app.extensions import db
from app.models.models import *
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print("🔄 Seeding all data...")
    
    # 1. Create Users
    print("\n📋 Creating Users...")
    
    users_data = [
        {
            "email": "admin@edo.gov.ng",
            "first_name": "Admin",
            "last_name": "User",
            "role": "Super Admin",
            "phone": "+234-800-ADMIN",
            "is_verified": True,
            "heritage_points": 1000,
            "bio": "Edo State Tourism Agency Administrator",
            "status": "active"
        },
        {
            "email": "tourist@gmail.com",
            "first_name": "Akenzua",
            "last_name": "Musa",
            "role": "Tourist",
            "phone": "+234-803-000-0001",
            "is_verified": True,
            "heritage_points": 75,
            "bio": "Tourism enthusiast exploring Edo State",
            "status": "active"
        },
        {
            "email": "jane@visitor.com",
            "first_name": "Jane",
            "last_name": "Williams",
            "role": "Tourist",
            "phone": "+234-803-000-0002",
            "is_verified": True,
            "heritage_points": 45,
            "bio": "Cultural heritage explorer",
            "status": "active"
        },
        {
            "email": "guide@edo.gov.ng",
            "first_name": "Osaro",
            "last_name": "Edokpayi",
            "role": "Guide",
            "phone": "+234-803-000-0003",
            "is_verified": True,
            "heritage_points": 200,
            "bio": "Professional tour guide specializing in Edo history",
            "status": "active"
        },
        {
            "email": "guide2@edo.gov.ng",
            "first_name": "Itohan",
            "last_name": "Omoruyi",
            "role": "Guide",
            "phone": "+234-803-000-0004",
            "is_verified": True,
            "heritage_points": 150,
            "bio": "Expert guide in Benin bronze casting and royal history",
            "status": "active"
        },
        {
            "email": "hotel@emotan.com",
            "first_name": "Emotan",
            "last_name": "Hotel",
            "role": "Hotel",
            "phone": "+234-803-000-0005",
            "is_verified": True,
            "status": "active"
        },
        {
            "email": "restaurant@mamaebo.com",
            "first_name": "Adaobi",
            "last_name": "Nwosu",
            "role": "Restaurant",
            "phone": "+234-803-000-0006",
            "is_verified": True,
            "status": "active"
        }
    ]
    
    created_users = {}
    for user_data in users_data:
        existing = User.query.filter_by(email=user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                phone=user_data.get("phone", ""),
                is_verified=user_data.get("is_verified", True),
                heritage_points=user_data.get("heritage_points", 0),
                bio=user_data.get("bio", ""),
                status=user_data.get("status", "active")
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            created_users[user_data["email"]] = user
            print(f"  ✅ Created user: {user_data['first_name']} {user_data['last_name']} ({user_data['role']})")
        else:
            created_users[user_data["email"]] = existing
            print(f"  ⏭️ User already exists: {user_data['email']}")
    
    # 2. Create Categories
    print("\n📋 Creating Categories...")
    
    categories_data = [
        {"name": "History & Museum", "type": "attraction", "icon": "bi-building-fill", "color": "#1a3a6b"},
        {"name": "UNESCO Heritage", "type": "attraction", "icon": "bi-globe", "color": "#c9a227"},
        {"name": "Nature & Wildlife", "type": "attraction", "icon": "bi-tree-fill", "color": "#2d8a4e"},
        {"name": "Adventure & Hiking", "type": "attraction", "icon": "bi-signpost-fill", "color": "#e05c27"},
    ]
    
    created_categories = {}
    for cat_data in categories_data:
        existing = Category.query.filter_by(name=cat_data["name"]).first()
        if not existing:
            cat = Category(**cat_data)
            db.session.add(cat)
            db.session.commit()
            created_categories[cat_data["name"]] = cat
            print(f"  ✅ Created category: {cat_data['name']}")
        else:
            created_categories[cat_data["name"]] = existing
            print(f"  ⏭️ Category already exists: {cat_data['name']}")
    
    # 3. Create Attractions
    print("\n📋 Creating Attractions...")
    
    attractions_data = [
        {
            "name": "The Royal Court of Benin (Oba's Palace)",
            "category_id": created_categories["History & Museum"].id,
            "description": "Rebuilt in 1915, this magnificent UNESCO-designated court serves as the sacred heart of Edo culture, housing ancient structures and historic court halls. A symbol of the Benin Kingdom's eternal sovereignty.",
            "address": "Oba's Palace Road, Benin City, Edo State",
            "history": "The original palace was destroyed during the British Punitive Expedition of 1897. The current structure was rebuilt in 1915 by Oba Eweka II and has been the official residence of the Oba of Benin ever since.",
            "opening_hours": "Daily 9AM–5PM",
            "ticket_price": 2000,
            "image_url": "https://images.unsplash.com/photo-1580654712603-eb43273aff33?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.3350,
            "longitude": 5.6037,
            "contact": "+234-52-260-200",
            "website": "https://edostate.gov.ng",
            "featured": True,
            "active": True,
            "views": 0,
            "status": "active"
        },
        {
            "name": "Igun Street Bronzecasting Guild",
            "category_id": created_categories["UNESCO Heritage"].id,
            "description": "Walk the ancient alley where master Benin bronze casters have worked for over 600 years. UNESCO-listed as Intangible Cultural Heritage. Watch artisans transform raw metal into masterworks.",
            "address": "Igun Street, Benin City, Edo State",
            "history": "The Igun Street bronze casting guild has been active since the 14th century. The traditional lost-wax casting technique has been passed down through generations of master craftsmen.",
            "opening_hours": "Mon–Sat 8AM–6PM",
            "ticket_price": 500,
            "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.3375,
            "longitude": 5.6050,
            "contact": "+234-52-260-201",
            "featured": True,
            "active": True,
            "views": 0,
            "status": "active"
        },
        {
            "name": "Okomu National Park",
            "category_id": created_categories["Nature & Wildlife"].id,
            "description": "One of the last surviving lowland tropical rainforests in Nigeria. Home to forest elephants, chimpanzees, white-throated monkeys, and hundreds of rare bird species.",
            "address": "Ovia South-West LGA, Edo State",
            "history": "Gazetted in 1935, Okomu was upgraded to full National Park status in 1999. It protects one of the most biodiverse ecosystems in West Africa.",
            "opening_hours": "Daily 7AM–5PM",
            "ticket_price": 3000,
            "image_url": "/static/uploads/attractions/3f382fd7edfe47f791adb21860e4dc53.jpg",
            "latitude": 6.2800,
            "longitude": 5.4500,
            "contact": "+234-52-260-202",
            "website": "https://okomu.nationalpark.gov.ng",
            "featured": True,
            "active": True,
            "views": 0,
            "status": "active"
        },
        {
            "name": "Ancient Benin Moats (Iya)",
            "category_id": created_categories["UNESCO Heritage"].id,
            "description": "The largest man-made earthworks in the world. Built over 1,000 years ago, these earthen walls protected the Benin Kingdom from invaders.",
            "address": "Ring Road, Benin City, Edo State",
            "history": "The Benin Moats were constructed by Oba Oguola in the 13th century and expanded by later Obas. The earthworks stretch for over 16 kilometers and were declared a UNESCO World Heritage site.",
            "opening_hours": "Sunrise to sunset",
            "ticket_price": 0,
            "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.3400,
            "longitude": 5.6300,
            "contact": "+234-52-260-203",
            "featured": False,
            "active": True,
            "views": 0,
            "status": "active"
        },
        {
            "name": "Osun Sacred Grove (Iguae-Okun)",
            "category_id": created_categories["History & Museum"].id,
            "description": "A sacred forest sanctuary dedicated to ancestral spirits and deities. Ancient shrines, towering trees, and a spiritual atmosphere make this a unique cultural experience.",
            "address": "GRA, Benin City, Edo State",
            "history": "The Osun Sacred Grove has been a site of worship and spiritual significance for centuries. It is one of the few remaining sacred groves in the region.",
            "opening_hours": "Daily 8AM–6PM",
            "ticket_price": 1000,
            "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.3450,
            "longitude": 5.6250,
            "featured": False,
            "active": True,
            "views": 0,
            "status": "active"
        },
        {
            "name": "Eki Market (Ring Road)",
            "category_id": created_categories["History & Museum"].id,
            "description": "A vibrant traditional market where locals gather to trade, socialize, and celebrate. Experience authentic Edo culture through food, crafts, and daily life.",
            "address": "Ring Road, Benin City, Edo State",
            "history": "Eki Market has been operating for over 50 years as the main trading hub in Benin City. It remains a vital center of commerce and cultural exchange.",
            "opening_hours": "Daily 6AM–8PM",
            "ticket_price": 0,
            "image_url": "/static/uploads/attractions/6f6220b5a6384eb184bf563976e0f203.jpg",
            "latitude": 6.3500,
            "longitude": 5.6200,
            "featured": False,
            "active": True,
            "views": 0,
            "status": "active"
        }
    ]
    
    created_attractions = {}
    for att_data in attractions_data:
        existing = Attraction.query.filter_by(name=att_data["name"]).first()
        if not existing:
            att = Attraction(**att_data)
            db.session.add(att)
            db.session.commit()
            created_attractions[att_data["name"]] = att
            print(f"  ✅ Created attraction: {att_data['name']}")
        else:
            created_attractions[att_data["name"]] = existing
            print(f"  ⏭️ Attraction already exists: {att_data['name']}")
    
    # 4. Create Guides
    print("\n📋 Creating Guides...")
    
    guide_user = User.query.filter_by(email="guide@edo.gov.ng").first()
    guide_user2 = User.query.filter_by(email="guide2@edo.gov.ng").first()
    
    if guide_user:
        existing = Guide.query.filter_by(user_id=guide_user.id).first()
        if not existing:
            guide = Guide(
                user_id=guide_user.id,
                phone="+234-803-000-0003",
                bio="Licensed Edo State Tour Guide specializing in Royal History, Igun Street Bronze guild, and the Oba's Palace. Over 8 years guiding international tourists.",
                languages="English, Edo, Pidgin, Yoruba",
                experience=8,
                hourly_rate=2500,
                daily_rate=15000,
                specializations="Royal History, Bronze Art, Heritage Sites",
                license_number="EDSTA-G-2018-001",
                verification_status="Approved",
                status="active"
            )
            db.session.add(guide)
            db.session.commit()
            print(f"  ✅ Created guide: Osaro Edokpayi")
        else:
            print(f"  ⏭️ Guide already exists: Osaro Edokpayi")
    
    if guide_user2:
        existing = Guide.query.filter_by(user_id=guide_user2.id).first()
        if not existing:
            guide2 = Guide(
                user_id=guide_user2.id,
                phone="+234-803-000-0004",
                bio="Certified tour guide with expertise in Benin bronze casting, cultural heritage, and UNESCO sites. Passionate about sharing Edo history.",
                languages="English, Edo, French",
                experience=5,
                hourly_rate=2000,
                daily_rate=12000,
                specializations="Bronze Casting, Cultural Heritage, UNESCO Sites",
                license_number="EDSTA-G-2021-004",
                verification_status="Approved",
                status="active"
            )
            db.session.add(guide2)
            db.session.commit()
            print(f"  ✅ Created guide: Itohan Omoruyi")
        else:
            print(f"  ⏭️ Guide already exists: Itohan Omoruyi")
    
    # 5. Create Hotels
    print("\n📋 Creating Hotels...")
    
    hotels_data = [
        {
            "name": "Emotan Hotel & Suites",
            "address": "3 Sapele Road, Benin City, Edo State",
            "description": "A premium 4-star hotel in the heart of Benin City's Government Reserved Area. Features exquisite Edo cultural décor, a rooftop bar with panoramic views, Olympic-standard pool, and world-class conference facilities.",
            "facilities": "WiFi, Pool, Gym, Restaurant, Bar, Conference Rooms, Parking",
            "price_per_night": 35000,
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.3350,
            "longitude": 5.6000,
            "contact": "+234-52-260-300",
            "website": "https://emotanhotel.com",
            "stars": 4,
            "total_rooms": 80,
            "featured": True,
            "status": "active"
        },
        {
            "name": "Royal Heritage Lodge",
            "address": "15 Airport Road, Benin City, Edo State",
            "description": "A boutique heritage lodge inspired by traditional Benin architecture. Each room features handcrafted brass decorations and traditional textiles. Experience royal hospitality.",
            "facilities": "WiFi, Parking, Garden, Restaurant, Cultural Tours",
            "price_per_night": 22000,
            "image_url": "https://images.unsplash.com/photo-1455587734955-081b22074882?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.3450,
            "longitude": 5.6150,
            "contact": "+234-52-260-301",
            "website": "https://royalheritagelodge.com",
            "stars": 3,
            "total_rooms": 25,
            "featured": True,
            "status": "active"
        },
        {
            "name": "Okomu Forest Resort",
            "address": "Okomu National Park, Ovia South-West LGA, Edo State",
            "description": "Immersive eco-resort on the edge of Okomu National Park. Luxury chalets nestled in the forest, guided dawn safaris, night nature walks, and an outdoor dining terrace overlooking the canopy.",
            "facilities": "WiFi, Pool, Restaurant, Nature Trails, Safaris, Spa",
            "price_per_night": 45000,
            "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.2800,
            "longitude": 5.4500,
            "contact": "+234-52-260-302",
            "website": "https://okomuresort.com",
            "stars": 4,
            "total_rooms": 30,
            "featured": True,
            "status": "active"
        }
    ]
    
    for hotel_data in hotels_data:
        existing = Hotel.query.filter_by(name=hotel_data["name"]).first()
        if not existing:
            hotel = Hotel(**hotel_data)
            db.session.add(hotel)
            db.session.commit()
            print(f"  ✅ Created hotel: {hotel_data['name']}")
        else:
            print(f"  ⏭️ Hotel already exists: {hotel_data['name']}")
    
    # 6. Create Restaurants
    print("\n📋 Creating Restaurants...")
    
    restaurants_data = [
        {
            "name": "Mama Ebo's Kitchen",
            "address": "15 Mission Road, Benin City, Edo State",
            "description": "Authentic Edo cuisine served in a warm, family-friendly environment. Known for traditional dishes like Edikang Ikong, Afang soup, and fresh seafood.",
            "cuisine": "Nigerian, Edo",
            "opening_hours": "Mon–Sat 10AM–10PM, Sun 12PM–8PM",
            "image_url": "https://images.unsplash.com/photo-1552566626-52f8b828add9?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.3400,
            "longitude": 5.6200,
            "contact": "+234-52-260-400",
            "price_range": "₦₦",
            "featured": True,
            "status": "active"
        },
        {
            "name": "Palace Grill",
            "address": "2 Oba's Palace Road, Benin City, Edo State",
            "description": "Fine dining with a royal touch. Enjoy exquisite continental and Nigerian dishes while overlooking the palace grounds. Perfect for special occasions.",
            "cuisine": "Continental, Nigerian",
            "opening_hours": "Tue–Sun 11AM–11PM",
            "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.3350,
            "longitude": 5.6037,
            "contact": "+234-52-260-401",
            "price_range": "₦₦₦",
            "featured": True,
            "status": "active"
        },
        {
            "name": "Okomu Bush Bar & Restaurant",
            "address": "Okomu National Park, Edo State",
            "description": "Rustic restaurant in the heart of the rainforest. Enjoy fresh local ingredients while listening to the sounds of the forest.",
            "cuisine": "Nigerian, Bushmeat",
            "opening_hours": "Daily 7AM–9PM",
            "image_url": "https://images.unsplash.com/photo-1544148103-0773bf10d330?auto=format&fit=crop&q=80&w=800",
            "latitude": 6.2800,
            "longitude": 5.4500,
            "contact": "+234-52-260-402",
            "price_range": "₦₦",
            "featured": False,
            "status": "active"
        }
    ]
    
    for rest_data in restaurants_data:
        existing = Restaurant.query.filter_by(name=rest_data["name"]).first()
        if not existing:
            rest = Restaurant(**rest_data)
            db.session.add(rest)
            db.session.commit()
            print(f"  ✅ Created restaurant: {rest_data['name']}")
        else:
            print(f"  ⏭️ Restaurant already exists: {rest_data['name']}")
    
    # 7. Create Events
    print("\n📋 Creating Events...")
    
    events_data = [
        {
            "name": "Igue Festival 2026",
            "description": "The most important festival in the Benin Kingdom. Features the Oba's ceremonial appearances, traditional dances, and cultural displays.",
            "date": datetime(2026, 12, 20, 9, 0, 0),
            "end_date": datetime(2026, 12, 30, 18, 0, 0),
            "location": "Oba's Palace, Benin City",
            "address": "Oba's Palace Road, Benin City",
            "image_url": "https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?auto=format&fit=crop&q=80&w=800",
            "ticket_price": 0,
            "capacity": 5000,
            "organizer": "Edo State Tourism Agency",
            "contact": "+234-52-260-500",
            "category": "Cultural Festival",
            "featured": True,
            "active": True,
            "latitude": 6.3350,
            "longitude": 5.6037,
            "status": "active"
        },
        {
            "name": "Okomu Eco-Safari Weekend",
            "description": "An immersive weekend exploring Okomu National Park. Includes guided safaris, night walks, bird watching, and conservation talks.",
            "date": datetime(2026, 8, 15, 6, 0, 0),
            "end_date": datetime(2026, 8, 17, 18, 0, 0),
            "location": "Okomu National Park",
            "address": "Ovia South-West LGA, Edo State",
            "image_url": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&q=80&w=800",
            "ticket_price": 15000,
            "capacity": 50,
            "organizer": "Okomu National Park Authority",
            "contact": "+234-52-260-501",
            "category": "Eco-tourism",
            "featured": True,
            "active": True,
            "latitude": 6.2800,
            "longitude": 5.4500,
            "status": "active"
        },
        {
            "name": "Benin Bronze Art Fair",
            "description": "Annual exhibition showcasing masterpieces from Igun Street bronze casters. Meet artisans, see demonstrations, and purchase authentic bronze works.",
            "date": datetime(2026, 10, 5, 10, 0, 0),
            "end_date": datetime(2026, 10, 12, 18, 0, 0),
            "location": "Ring Road Exhibition Centre, Benin City",
            "address": "Ring Road, Benin City",
            "image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&q=80&w=800",
            "ticket_price": 5000,
            "capacity": 2000,
            "organizer": "Igun Street Bronze Guild",
            "contact": "+234-52-260-502",
            "category": "Art & Culture",
            "featured": False,
            "active": True,
            "latitude": 6.3400,
            "longitude": 5.6200,
            "status": "active"
        }
    ]
    
    for event_data in events_data:
        existing = Event.query.filter_by(name=event_data["name"]).first()
        if not existing:
            event = Event(**event_data)
            db.session.add(event)
            db.session.commit()
            print(f"  ✅ Created event: {event_data['name']}")
        else:
            print(f"  ⏭️ Event already exists: {event_data['name']}")
    
    # 8. Create Reviews
    print("\n📋 Creating Reviews...")
    
    tourist = User.query.filter_by(email="tourist@gmail.com").first()
    jane = User.query.filter_by(email="jane@visitor.com").first()
    
    if tourist and created_attractions:
        # Review for Okomu National Park
        existing = Review.query.filter_by(user_id=tourist.id, target_type="Attraction", target_id=created_attractions["Okomu National Park"].id).first()
        if not existing:
            review = Review(
                user_id=tourist.id,
                target_type="Attraction",
                target_id=created_attractions["Okomu National Park"].id,
                rating=4,
                comment="Amazing wildlife and beautiful forest! The guides were knowledgeable and friendly.",
                is_approved=True,
                status="active"
            )
            db.session.add(review)
            print(f"  ✅ Created review: Okomu National Park (4 stars)")
        
        # Review for Royal Court
        existing = Review.query.filter_by(user_id=tourist.id, target_type="Attraction", target_id=created_attractions["The Royal Court of Benin (Oba's Palace)"].id).first()
        if not existing:
            review2 = Review(
                user_id=tourist.id,
                target_type="Attraction",
                target_id=created_attractions["The Royal Court of Benin (Oba's Palace)"].id,
                rating=5,
                comment="Incredible historical experience! The palace grounds are breathtaking.",
                is_approved=True,
                status="active"
            )
            db.session.add(review2)
            print(f"  ✅ Created review: Royal Court (5 stars)")
    
    if jane and created_attractions:
        # Review for Igun Street
        existing = Review.query.filter_by(user_id=jane.id, target_type="Attraction", target_id=created_attractions["Igun Street Bronzecasting Guild"].id).first()
        if not existing:
            review3 = Review(
                user_id=jane.id,
                target_type="Attraction",
                target_id=created_attractions["Igun Street Bronzecasting Guild"].id,
                rating=5,
                comment="Watching the bronze casters at work is mesmerizing. A must-see in Benin City!",
                is_approved=True,
                status="active"
            )
            db.session.add(review3)
            print(f"  ✅ Created review: Igun Street (5 stars)")
    
    db.session.commit()
    
    print("\n" + "="*50)
    print("✅ ALL DATA SEEDED SUCCESSFULLY!")
    print("="*50)
    print("\n📋 Summary:")
    print(f"   Users: {User.query.count()}")
    print(f"   Categories: {Category.query.count()}")
    print(f"   Attractions: {Attraction.query.count()}")
    print(f"   Guides: {Guide.query.count()}")
    print(f"   Hotels: {Hotel.query.count()}")
    print(f"   Restaurants: {Restaurant.query.count()}")
    print(f"   Events: {Event.query.count()}")
    print(f"   Reviews: {Review.query.count()}")
    print("\n🔑 Login Credentials:")
    print("   Admin: admin@edo.gov.ng / password123")
    print("   Tourist: tourist@gmail.com / password123")
    print("   Guide: guide@edo.gov.ng / password123")
    print("   Hotel: hotel@emotan.com / password123")
    print("   Restaurant: restaurant@mamaebo.com / password123")