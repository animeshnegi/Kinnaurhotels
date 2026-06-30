from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

# ---------- Shared site data ----------
SITE = {
    "phone": "70184-91169",          # same number for cafe + homestay
    "whatsapp": "7018491169",
    "email": "kinnaurhotels@gmail.com",
    "address": "The Bait, Reckong Peo, Kinnaur, Himachal Pradesh 172107",
    "google_rating_cafe": 4.9,
    "google_reviews_cafe": 60,
    "google_rating_homestay": 4.8,
    "google_reviews_homestay": 10,
    "maps_link_cafe": "https://www.google.com/search?q=the+bait+reckong+peo",
    "maps_link_homestay": "https://www.google.com/search?q=holasay+homestay+kalpa",
}

CAFE_REVIEWS = [
    {"name": "Sharvan Negi", "text": "Best food in Kalpa region — fresh, warm and full of flavor. Loved the cosy mountain-view seating.", "rating": 5},
    {"name": "Eami Thakur", "text": "Such a friendly staff and great presentation. A must-visit cafe near Reckong Peo market.", "rating": 5},
    {"name": "Rahul Verma", "text": "Stopped here while travelling to Kalpa — easily the best local food experience in Kinnaur.", "rating": 4},
]

HOMESTAY_REVIEWS = [
    {"name": "Priya Sharma", "text": "Holasay Homestay gave us the warmest Kinnauri hospitality with stunning views of the Kinner Kailash range.", "rating": 5},
    {"name": "Aman Gupta", "text": "Clean rooms, home-cooked local food and a peaceful stay in Kalpa. Highly recommended homestay near Reckong Peo.", "rating": 5},
    {"name": "Neha Kapoor", "text": "Felt like home. The hosts shared great tips on local sightseeing around Kalpa and Kinnaur.", "rating": 4},
]

CAFE_MENU = [
    {"category": "Beverages", "dishes": [
        ("Butter Tea"), ("Masala Tea"), ("Cofee"), ("Cold Coffee"), ("Coldrinks")
    ]},
    {"category": "Local & Comfort Food", "dishes": [
        ("kinnauri Rajma Rice"), ("Momos (Veg/Non-Veg)"), ("Thukpa"),
        ("Parantha (pyaz/aalu/paneer)"), ("Noodles"), ("Local Lamb Curry"), ("Chilta (Buck Wheat)"), ("Local vegitable curry")
    ]}

]

ROOM_TYPES = [
    {"name": "Single Room", "price": "₹2,200/night", "desc": "Travelling solo? Our cosy single room is perfect for a comfortable stay with a view of Kinner Kailash.","img": "/static/images/holasay_homestay/room2.jpg"},
    {"name": "Deluxe Family Room", "price": "₹3,200/night", "desc": "Spacious room for families, well spacious perfect for family of four.","img": "/static/images/holasay_homestay/room1.jpg"},
    {"name": "Kinnaur kailash View", "price": "₹2,800/night", "desc": "Cosy room with direct views of Kinner Kailash, attached bath, and Delicious Kinnauri cuisine.","img": "/static/images/holasay_homestay/mountain_view.jpg"},
]

CAFE_LOCAL_FOOD = [
    {"title": "Kinnauri Rajma Rice", "desc": "A beloved Himalayan comfort meal pairing smooth, high-altitude red kidney beans with steamed rice", "img": "/static/images/food/kinnauri_rajma_rice.jpg"},
    {"title": "Kinnauri Thukpa", "desc": "A hearty Himalayan noodle soup, slow-simmered with local herbs and vegetables — a Kalpa winter favourite.", "img": "/static/images/food/thukpa.jpg"},
    {"title": "Chilta", "desc": "Kinnauri Chilta is a traditional flatbread prepared from locally grown buckwheat (Ogla or Kuttu), reflecting the rich agricultural heritage of Kinnaur", "img": "/static/images/food/chilta.jpg"},
    {"title": "Kinnauri Gucchi – Morel Mushroom curry", "desc": "A traditional delicacy made from prized morel mushrooms, handpicked from the forests of the Himalayan region", "img": "/static/images/food/kinnauri_gucchi.jpg"},
]

CAFE_SPECIALITIES = [
    {"icon": "☕", "title": "Best Coffee", "desc": "coffee perfect with a Kinnaur Kailash mountain view."},
    {"icon": "🥟", "title": "Steamed Momos", "desc": "Soft, juicy veg and chicken momos made fresh to order, a cafe favourite."},
    {"icon": "🍞", "title": "Local Food", "desc": "From wholesome buckwheat preparations like Kinnauri Chilta to delicacies such as Gucchi (morel mushroom) curry, Kinnauri food celebrates simplicity, nutrition, and the unique taste of the Himalayas."},
    {"icon": "🍎", "title": "Local Apple Delicacies", "desc": "Desserts and drinks made using apples straight from Kinnaur's orchards."},
]

HOMESTAY_SPECIALITIES = [
    {"icon": "🏡", "title": "Family-Run Hospitality", "desc": "A genuine, warm welcome from a local Kinnauri family who treat guests like their own."},
    {"icon": "🍲", "title": "Home-Cooked Meals", "desc": "Traditional Kinnauri thalis cooked fresh daily using local, seasonal ingredients."},
    {"icon": "🌄", "title": "Sunrise Views", "desc": "Wake up to golden sunrise light over the Kinner Kailash range from your room."},
    {"icon": "🍏", "title": "Orchard Walks", "desc": "Guided walks through Holasay's own apple orchards, right outside your door."},
]

MOUNTAIN_VIEW_INFO = {
    "title": "Kinner Kailash View",
    "desc": "Holasay Homestay sits at a vantage point in Kalpa with an uninterrupted, postcard-perfect view of the sacred Kinner Kailash peak (6,050m). Watch the peak glow gold at sunrise and sunset — one of the most photographed views in all of Kinnaur, right from your balcony.",
    "img": "/static/images/holasay_homestay/mountain_view.jpg",
}

KINNAUR_LOCAL_SPECIALITIES = [
    {"title": "Chilgoza Pine Nuts", "desc": "Kinnaur is famous across India for its prized chilgoza (pine nuts), hand-harvested from the region's chilgoza forests.", "img": "/static/images/food/pine_seed.jpg"},
    {"title": "Kinnauri Rajma", "desc": "A local variety of kidney beans grown in Kinnaur's high-altitude fields, cooked into a rich, hearty curry.", "img": "/static/images/food/rajma_rice.jpg"},
    {"title": "Churpi (Local Cheese)", "desc": "A traditional fermented dairy product from Kinnaur and the wider Himalayan belt, eaten as a snack or added to dishes.", "img": "/static/images/food/churpi.jpg"},
    {"title": "Kalpa Apple Products", "desc": "From fresh apples to jams, ciders and pies — Kalpa's orchards supply some of Himachal's best apples.", "img": "/static/images/food/apple_pro.jpg"},
    {"title": "Angoori (Local Grape Wine)", "desc": "A mildly fermented local grape drink traditionally made in Kinnauri households, often shared during festivals.", "img": "/static/images/food/local_wine_grape.jpg"},
    {"title": "Til Chutney", "desc": "A nutty, spicy sesame-seed chutney that's a staple accompaniment in most Kinnauri meals.", "img": "/static/images/food/til_chutney.jpg"},
]

# ---------- Blog content: Kinnaur travel & culture ----------
BLOG_POSTS = [
    {
        "slug": "kinner-kailash-trek-guide",
        "title": "Kinner Kailash Trek: Complete Guide From Kalpa & Reckong Peo",
        "category": "Trekking",
        "date": "June 2026",
        "image": "/static/images/blog/kinnaur_kailash_shivling.jpg",
        "excerpt": "Everything you need to know before attempting the sacred Kinner Kailash trek — route, best season, permits, and where to stay before and after.",
        "content": [
            "The Kinner Kailash trek is one of the most revered high-altitude treks in Himachal Pradesh, circling the sacred Kinner Kailash peak (6,050m) which is worshipped by both Hindus and Buddhists. The trek typically begins from Tangling village near Kalpa and takes 4 to 6 days to complete, depending on the route and acclimatisation stops.",
            "The best season to attempt the Kinner Kailash trek is between June and October, after the snow has melted enough to make the high passes accessible. Trekkers usually base themselves in Kalpa or Reckong Peo a day or two before starting, both to acclimatise and to arrange local guides and permits through the Kinnaur district forest office.",
            "Along the way, you'll pass alpine meadows, the holy Parvati Kund lake, and finally the Shivling — a natural rock formation believed to resemble a Shiva lingam, visible from the base of the peak. Many trekkers time their trip around the Kinner Kailash Yatra in August, when groups undertake a parikrama (circumambulation) of the peak.",
            "Where to stay: Kalpa and Reckong Peo are the natural base points. A homestay like Holasay Homestay offers acclimatisation comfort with direct views of the very peak you're about to trek toward, along with home-cooked local food to fuel up before the climb. After the trek, there's nothing better than warming up with a hot meal at The Bait Cafe in Reckong Peo.",
        ],
    },
    {
        "slug": "fulaich-festival-kinnaur",
        "title": "Fulaich Festival: The Flower Festival of Kinnaur",
        "category": "Culture & Festivals",
        "date": "May 2026",
        "image": "/static/images/blog/fulaich_festival.jpg",
        "excerpt": "Discover Fulaich, Kinnaur's colourful flower festival, celebrated to honour ancestors and welcome the harvest season.",
        "content": [
            "Fulaich (also spelled Phulaich or Phulech) is one of Kinnaur's most important local festivals, celebrated by villages across the district including areas around Kalpa and Reckong Peo. The festival is dedicated to honouring ancestors and deities, and marks a turning point in the agricultural calendar.",
            "During Fulaich, villagers trek up to high alpine meadows to collect a special wildflower, locally believed to carry blessings. These flowers are brought back down to the village amid much fanfare — drums, traditional Kinnauri dance, and song accompany the procession.",
            "The festival usually unfolds over multiple days, with each day dedicated to a different ritual: flower collection, a community feast featuring local food, and finally a celebratory dance where the whole village participates in traditional Kinnauri attire.",
            "If you're visiting Kalpa or Reckong Peo around the festival dates (these vary slightly by village and lunar calendar, generally around September), it's a wonderful time to experience authentic Kinnauri culture. Pair your visit with a stay at Holasay Homestay, where hosts can often point you toward the nearest village celebrations.",
        ],
    },
    {
        "slug": "ralane-fair-kinnaur",
        "title": "Raulane Fair: Kinnaur's Traditional Mela",
        "category": "Culture & Festivals",
        "date": "April 2026",
        "image": "/static/images/blog/raulane_festival.jpg",
        "excerpt": "An inside look at the Raulane fair — a traditional gathering of Kinnauri communities filled with music, dance, and local food.",
        "content": [
            "The Raulane fair is a traditional community gathering held in parts of Kinnaur, bringing together villagers for a celebration that blends religious ritual with social festivity. Like many Himalayan melas, it serves both a spiritual purpose — invoking local deities for protection and a good harvest — and a social one, reuniting families and neighbouring villages.",
            "Expect vibrant Kinnauri dance circles, traditional drum and flute music (the dhol and shehnai), and stalls selling local handicrafts, woollens, and seasonal produce. Local food is, unsurprisingly, central to the celebration — expect to be offered Kinnauri thalis, sweets, and the local grape drink, angoori.",
            "For travellers, attending a fair like Raulane offers a rare window into Kinnaur's living culture beyond the tourist trail of Kalpa's apple orchards and mountain views. Ask locally in Reckong Peo for the nearest village celebrating it during your visit — your homestay hosts at Holasay are often your best source for up-to-date dates.",
        ],
    },
    {
        "slug": "best-local-food-kalpa",
        "title": "Best Local Food to Try in Kalpa & Reckong Peo",
        "category": "Food",
        "date": "March 2026",
        "image": "https://picsum.photos/seed/kalpafoodblog/1000/650",
        "excerpt": "From Kinnauri thukpa to chilgoza pine nuts — here's a foodie's guide to the best local food in Kalpa and Reckong Peo.",
        "content": [
            "Kinnaur's food culture is shaped by its high-altitude geography — hearty, warming dishes, dried and fermented preservation techniques, and a strong reliance on locally grown grains, legumes, and fruit. If you're visiting Kalpa or Reckong Peo, here are the dishes you shouldn't miss.",
            "Start with Thukpa — a noodle soup that's perfect for the cold mountain air, available at most local eateries including The Bait Cafe. Follow it up with Chha Gosht, a tangy curd-based mutton curry that's a Kinnauri classic, or Sattu Roti for something simpler and equally satisfying.",
            "Don't leave without trying Kinnaur's famous chilgoza (pine nuts) and, if you're visiting in apple season, the region's renowned apples straight from Kalpa's orchards — used in everything from fresh fruit to pies and ciders at local cafes.",
            "For an at-home experience of authentic Kinnauri cooking, a homestay stay is unbeatable — Holasay Homestay serves home-cooked meals using ingredients sourced from its own orchards and the surrounding valley.",
        ],
    },
    {
        "slug": "things-to-do-kalpa-reckong-peo",
        "title": "Things to Do in Kalpa & Reckong Peo: A Travel Guide",
        "category": "Travel Guide",
        "date": "February 2026",
        "image": "https://picsum.photos/seed/kalpatravelguide/1000/650",
        "excerpt": "A practical guide to sightseeing, food, and stays around Kalpa and Reckong Peo, Kinnaur's scenic district headquarters.",
        "content": [
            "Reckong Peo, the district headquarters of Kinnaur, and Kalpa, the scenic village just above it, together make one of Himachal Pradesh's most rewarding less-crowded destinations. Here's how to make the most of a visit.",
            "Start your day with a coffee and breakfast at The Bait Cafe in Reckong Peo before heading up to Kalpa — the drive alone offers sweeping views of the Sutlej valley. In Kalpa, visit the old Kalpa village with its traditional wooden architecture, the Chandika Devi temple, and the Buddhist monastery.",
            "The single best experience in Kalpa, though, is simply waking up to the sunrise over Kinner Kailash — best enjoyed from a homestay balcony rather than a hotel room. Holasay Homestay is positioned for exactly this view.",
            "Round off your trip with a stroll through Kalpa's apple orchards (best in September-October during harvest), and a final local meal back at The Bait Cafe before heading onward to Sangla, Chitkul, or back down to Shimla.",
        ],
    },
]




@app.route("/")
def home():
    return render_template(
        "index.html",
        site=SITE,
        cafe_reviews=CAFE_REVIEWS,
        homestay_reviews=HOMESTAY_REVIEWS,
        cafe_local_food=CAFE_LOCAL_FOOD,
        cafe_specialities=CAFE_SPECIALITIES,
        homestay_specialities=HOMESTAY_SPECIALITIES,
        mountain_view=MOUNTAIN_VIEW_INFO,
        menu=CAFE_MENU,
        rooms=ROOM_TYPES,
        kinnaur_specialities=KINNAUR_LOCAL_SPECIALITIES,
        blog_posts=BLOG_POSTS[:3],
    )


@app.route("/blog")
def blog_list():
    return render_template("blog_list.html", site=SITE, posts=BLOG_POSTS)


@app.route("/blog/<slug>")
def blog_detail(slug):
    post = next((p for p in BLOG_POSTS if p["slug"] == slug), None)
    if not post:
        return redirect(url_for("blog_list"))
    related = [p for p in BLOG_POSTS if p["slug"] != slug][:3]
    return render_template("blog_detail.html", site=SITE, post=post, related=related)


@app.route("/robots.txt")
def robots():
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.url_root.rstrip('/')}/sitemap.xml",
    ]
    return "\n".join(lines), 200, {"Content-Type": "text/plain"}


@app.route("/sitemap.xml")
def sitemap():
    pages = ["home", "cafe", "homestay", "menu", "booking", "contact", "blog_list"]
    urls = [request.url_root.rstrip("/") + url_for(p) for p in pages]
    urls += [request.url_root.rstrip("/") + url_for("blog_detail", slug=p["slug"]) for p in BLOG_POSTS]
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        xml.append(f"<url><loc>{u}</loc></url>")
    xml.append("</urlset>")
    return "\n".join(xml), 200, {"Content-Type": "application/xml"}


@app.route("/cafe")
def cafe():
    return render_template("cafe.html", site=SITE, reviews=CAFE_REVIEWS)


@app.route("/homestay")
def homestay():
    return render_template("homestay.html", site=SITE, reviews=HOMESTAY_REVIEWS, rooms=ROOM_TYPES)


@app.route("/menu")
def menu():
    return render_template("menu.html", site=SITE, menu=CAFE_MENU)


@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form.get("name")
        booking_type = request.form.get("booking_type")
        date = request.form.get("date")
        guests = request.form.get("guests")
        phone = request.form.get("phone")
        # NOTE: hook this up to email/DB/WhatsApp API as needed
        flash(f"Thank you {name}! Your {booking_type} request for {date} ({guests} guests) has been received. We'll call you at {phone} shortly.", "success")
        return redirect(url_for("booking"))
    return render_template("booking.html", site=SITE)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks for reaching out! We'll get back to you soon.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", site=SITE)


if __name__ == "__main__":
    app.run(debug=True)
