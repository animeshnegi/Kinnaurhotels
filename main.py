from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import json
from pathlib import Path
from functools import wraps
from datetime import datetime
import uuid
import re
import requests

app = Flask(__name__)
app.secret_key = "AnimeshNegi007"

CONFIG_FILE = Path("config/config.json")
ADMIN_PASSWORD = "admin123"

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(data):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_slug(title):
    """Generate a URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug

def send_email(name, date, guests, phone, booking_type):
    """Send email notification for bookings"""
    config = load_config()
    mail_api = config.get("MAIL_API", {})
    
    if not mail_api.get("api_key"):
        return False
    
    html_template = """
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #1e3a8a, #2563eb); color: white; padding: 20px;">
            <h2 style="margin: 0;">🏔️ New Booking Received</h2>
        </div>
        <div style="padding: 24px; color: #374151; line-height: 1.7;">
            <p>Hello,</p>
            <p>A new booking request has been received from the website.</p>
            <div style="background: #f8fafc; border-left: 4px solid #2563eb; padding: 16px; border-radius: 8px;">
                <p style="margin: 6px 0;"><strong>Guest Name:</strong> {{name}}</p>
                <p style="margin: 6px 0;"><strong>Total Guests:</strong> {{guests}}</p>
                <p style="margin: 6px 0;"><strong>Date:</strong> {{date}}</p>
                <p style="margin: 6px 0;"><strong>Booking Type:</strong> {{booking_type}}</p>
                <p style="margin: 6px 0;"><strong>Phone:</strong> {{phone}}</p>
            </div>
            <p style="margin-top: 20px;">You can contact the guest directly at <strong style="color: #2563eb;">{{phone}}</strong> to confirm the booking.</p>
        </div>
        <div style="background: #f3f4f6; padding: 14px; text-align: center; color: #6b7280; font-size: 13px;">Kinnaur Hotels &bull; Website Booking Notification</div>
    </div>
    """
    
    personalized_body_html = html_template.replace("{{name}}", name).replace("{{date}}", date).replace("{{guests}}", guests).replace("{{phone}}", phone).replace("{{booking_type}}", booking_type)
    subject = f"New Reservation from {name}"

    payload = {
        "apikey": mail_api.get("api_key"),
        "subject": subject,
        "from": mail_api.get("from_email", "Mike@engineer-ip.com"),
        "to": mail_api.get("to_email"),
        "bodyText": "Received New Booking Request",
        "bodyHtml": personalized_body_html,
        "isTransactional": True
    }

    try:
        response = requests.post(mail_api.get("api_url", ""), data=payload)
        return response.status_code == 200
    except:
        return False

config = load_config()

SITE = config["SITE"]
CAFE_REVIEWS = config["CAFE_REVIEWS"]
HOMESTAY_REVIEWS = config["HOMESTAY_REVIEWS"]
CAFE_MENU = config["CAFE_MENU"]
ROOM_TYPES = config["ROOM_TYPES"]
CAFE_LOCAL_FOOD = config["CAFE_LOCAL_FOOD"]
CAFE_SPECIALITIES = config["CAFE_SPECIALITIES"]
HOMESTAY_SPECIALITIES = config["HOMESTAY_SPECIALITIES"]
MOUNTAIN_VIEW_INFO = config["MOUNTAIN_VIEW_INFO"]
KINNAUR_LOCAL_SPECIALITIES = config["KINNAUR_LOCAL_SPECIALITIES"]
BLOG_POSTS = config["BLOG_POSTS"]

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
        send_email(name, date, guests, phone, booking_type)
        flash(f"Thank you {name}! Your {booking_type} request for {date} ({guests} guests) has been received. We'll call you at {phone} shortly.", "success")
        return redirect(url_for("contact"))
    return render_template("booking.html", site=SITE)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        send_email(name, email, subject, message, "Contact Form")
        flash("Thanks for reaching out! We'll get back to you soon.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", site=SITE)

# ============== ADVANCED ADMIN PANEL ==============

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid password", "error")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))

@app.route("/admin")
@login_required
def admin_dashboard():
    from datetime import datetime
    config_data = load_config()
    stats = {
        "total_blogs": len(config_data.get("BLOG_POSTS", [])),
        "total_reviews": len(config_data.get("CAFE_REVIEWS", [])) + len(config_data.get("HOMESTAY_REVIEWS", [])),
        "total_menu_items": sum(len(c.get("dishes", [])) for c in config_data.get("CAFE_MENU", [])),
        "total_rooms": len(config_data.get("ROOM_TYPES", [])),
        "total_specialities": len(config_data.get("CAFE_SPECIALITIES", [])) + len(config_data.get("HOMESTAY_SPECIALITIES", [])),
    }
    return render_template("admin/dashboard.html", stats=stats, site=SITE, current_date=datetime.now().strftime('%B %d, %Y'))

# ===== BLOG MANAGEMENT =====

@app.route("/admin/blogs")
@login_required
def admin_blogs():
    config_data = load_config()
    blogs = config_data.get("BLOG_POSTS", [])
    return render_template("admin/blogs.html", blogs=blogs, site=SITE)

@app.route("/admin/blog/add", methods=["GET", "POST"])
@login_required
def admin_blog_add():
    if request.method == "POST":
        try:
            config_data = load_config()
            blogs = config_data.get("BLOG_POSTS", [])
            
            title = request.form.get("title")
            category = request.form.get("category")
            date = request.form.get("date")
            image = request.form.get("image")
            excerpt = request.form.get("excerpt")
            content_lines = request.form.get("content").split('\n')
            content = [line.strip() for line in content_lines if line.strip()]
            
            slug = generate_slug(title)
            
            # Check if slug already exists
            if any(b["slug"] == slug for b in blogs):
                slug = f"{slug}-{uuid.uuid4().hex[:6]}"
            
            new_blog = {
                "slug": slug,
                "title": title,
                "category": category,
                "date": date,
                "image": image,
                "excerpt": excerpt,
                "content": content
            }
            
            blogs.append(new_blog)
            config_data["BLOG_POSTS"] = blogs
            save_config(config_data)
            
            # Reload global variable
            global BLOG_POSTS
            BLOG_POSTS = blogs
            
            flash("Blog post created successfully!", "success")
            return redirect(url_for('admin_blogs'))
        except Exception as e:
            flash(f"Error creating blog: {str(e)}", "error")
            return redirect(url_for('admin_blog_add'))
    
    return render_template("admin/blog_form.html", blog=None, site=SITE, action="Add")

@app.route("/admin/blog/edit/<slug>", methods=["GET", "POST"])
@login_required
def admin_blog_edit(slug):
    config_data = load_config()
    blogs = config_data.get("BLOG_POSTS", [])
    blog_index = next((i for i, b in enumerate(blogs) if b["slug"] == slug), None)
    
    if blog_index is None:
        flash("Blog post not found", "error")
        return redirect(url_for('admin_blogs'))
    
    if request.method == "POST":
        try:
            title = request.form.get("title")
            category = request.form.get("category")
            date = request.form.get("date")
            image = request.form.get("image")
            excerpt = request.form.get("excerpt")
            content_lines = request.form.get("content").split('\n')
            content = [line.strip() for line in content_lines if line.strip()]
            
            new_slug = generate_slug(title)
            
            # Update blog
            blogs[blog_index] = {
                "slug": new_slug,
                "title": title,
                "category": category,
                "date": date,
                "image": image,
                "excerpt": excerpt,
                "content": content
            }
            
            config_data["BLOG_POSTS"] = blogs
            save_config(config_data)
            
            global BLOG_POSTS
            BLOG_POSTS = blogs
            
            flash("Blog post updated successfully!", "success")
            return redirect(url_for('admin_blogs'))
        except Exception as e:
            flash(f"Error updating blog: {str(e)}", "error")
    
    blog = blogs[blog_index]
    return render_template("admin/blog_form.html", blog=blog, site=SITE, action="Edit")

@app.route("/admin/blog/delete/<slug>", methods=["POST"])
@login_required
def admin_blog_delete(slug):
    try:
        config_data = load_config()
        blogs = config_data.get("BLOG_POSTS", [])
        blogs = [b for b in blogs if b["slug"] != slug]
        config_data["BLOG_POSTS"] = blogs
        save_config(config_data)
        
        global BLOG_POSTS
        BLOG_POSTS = blogs
        
        flash("Blog post deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting blog: {str(e)}", "error")
    
    return redirect(url_for('admin_blogs'))

# ===== REVIEW MANAGEMENT =====

@app.route("/admin/reviews")
@login_required
def admin_reviews():
    config_data = load_config()
    cafe_reviews = config_data.get("CAFE_REVIEWS", [])
    homestay_reviews = config_data.get("HOMESTAY_REVIEWS", [])
    return render_template("admin/reviews.html", cafe_reviews=cafe_reviews, homestay_reviews=homestay_reviews, site=SITE)

@app.route("/admin/review/add", methods=["POST"])
@login_required
def admin_review_add():
    try:
        config_data = load_config()
        review_type = request.form.get("review_type")
        name = request.form.get("name")
        text = request.form.get("text")
        rating = int(request.form.get("rating"))
        
        new_review = {
            "name": name,
            "text": text,
            "rating": rating
        }
        
        if review_type == "cafe":
            config_data["CAFE_REVIEWS"].append(new_review)
            global CAFE_REVIEWS
            CAFE_REVIEWS = config_data["CAFE_REVIEWS"]
        else:
            config_data["HOMESTAY_REVIEWS"].append(new_review)
            global HOMESTAY_REVIEWS
            HOMESTAY_REVIEWS = config_data["HOMESTAY_REVIEWS"]
        
        save_config(config_data)
        flash("Review added successfully!", "success")
    except Exception as e:
        flash(f"Error adding review: {str(e)}", "error")
    
    return redirect(url_for('admin_reviews'))

@app.route("/admin/review/delete/<review_type>/<int:index>", methods=["POST"])
@login_required
def admin_review_delete(review_type, index):
    try:
        config_data = load_config()
        
        if review_type == "cafe":
            if 0 <= index < len(config_data["CAFE_REVIEWS"]):
                del config_data["CAFE_REVIEWS"][index]
                global CAFE_REVIEWS
                CAFE_REVIEWS = config_data["CAFE_REVIEWS"]
        else:
            if 0 <= index < len(config_data["HOMESTAY_REVIEWS"]):
                del config_data["HOMESTAY_REVIEWS"][index]
                global HOMESTAY_REVIEWS
                HOMESTAY_REVIEWS = config_data["HOMESTAY_REVIEWS"]
        
        save_config(config_data)
        flash("Review deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting review: {str(e)}", "error")
    
    return redirect(url_for('admin_reviews'))

# ===== MENU MANAGEMENT =====

@app.route("/admin/menu")
@login_required
def admin_menu():
    config_data = load_config()
    menu = config_data.get("CAFE_MENU", [])
    return render_template("admin/menu.html", menu=menu, site=SITE)

@app.route("/admin/menu/category/add", methods=["POST"])
@login_required
def admin_menu_category_add():
    try:
        config_data = load_config()
        category_name = request.form.get("category_name")
        
        new_category = {
            "category": category_name,
            "dishes": []
        }
        
        config_data["CAFE_MENU"].append(new_category)
        save_config(config_data)
        
        global CAFE_MENU
        CAFE_MENU = config_data["CAFE_MENU"]
        
        flash("Category added successfully!", "success")
    except Exception as e:
        flash(f"Error adding category: {str(e)}", "error")
    
    return redirect(url_for('admin_menu'))

@app.route("/admin/menu/category/delete/<int:index>", methods=["POST"])
@login_required
def admin_menu_category_delete(index):
    try:
        config_data = load_config()
        if 0 <= index < len(config_data["CAFE_MENU"]):
            del config_data["CAFE_MENU"][index]
            save_config(config_data)
            global CAFE_MENU
            CAFE_MENU = config_data["CAFE_MENU"]
            flash("Category deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting category: {str(e)}", "error")
    
    return redirect(url_for('admin_menu'))

@app.route("/admin/menu/dish/add", methods=["POST"])
@login_required
def admin_menu_dish_add():
    try:
        config_data = load_config()
        category_index = int(request.form.get("category_index"))
        dish_name = request.form.get("dish_name")
        
        if 0 <= category_index < len(config_data["CAFE_MENU"]):
            config_data["CAFE_MENU"][category_index]["dishes"].append(dish_name)
            save_config(config_data)
            global CAFE_MENU
            CAFE_MENU = config_data["CAFE_MENU"]
            flash("Dish added successfully!", "success")
    except Exception as e:
        flash(f"Error adding dish: {str(e)}", "error")
    
    return redirect(url_for('admin_menu'))

@app.route("/admin/menu/dish/delete", methods=["POST"])
@login_required
def admin_menu_dish_delete():
    try:
        config_data = load_config()
        category_index = int(request.form.get("category_index"))
        dish_index = int(request.form.get("dish_index"))
        
        if 0 <= category_index < len(config_data["CAFE_MENU"]):
            if 0 <= dish_index < len(config_data["CAFE_MENU"][category_index]["dishes"]):
                del config_data["CAFE_MENU"][category_index]["dishes"][dish_index]
                save_config(config_data)
                global CAFE_MENU
                CAFE_MENU = config_data["CAFE_MENU"]
                flash("Dish deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting dish: {str(e)}", "error")
    
    return redirect(url_for('admin_menu'))

# ===== ROOM MANAGEMENT =====

@app.route("/admin/rooms")
@login_required
def admin_rooms():
    config_data = load_config()
    rooms = config_data.get("ROOM_TYPES", [])
    return render_template("admin/rooms.html", rooms=rooms, site=SITE)

@app.route("/admin/room/add", methods=["POST"])
@login_required
def admin_room_add():
    try:
        config_data = load_config()
        name = request.form.get("name")
        price = request.form.get("price")
        desc = request.form.get("desc")
        img = request.form.get("img")
        
        new_room = {
            "name": name,
            "price": price,
            "desc": desc,
            "img": img
        }
        
        config_data["ROOM_TYPES"].append(new_room)
        save_config(config_data)
        
        global ROOM_TYPES
        ROOM_TYPES = config_data["ROOM_TYPES"]
        
        flash("Room added successfully!", "success")
    except Exception as e:
        flash(f"Error adding room: {str(e)}", "error")
    
    return redirect(url_for('admin_rooms'))

@app.route("/admin/room/edit/<int:index>", methods=["POST"])
@login_required
def admin_room_edit(index):
    try:
        config_data = load_config()
        if 0 <= index < len(config_data["ROOM_TYPES"]):
            config_data["ROOM_TYPES"][index] = {
                "name": request.form.get("name"),
                "price": request.form.get("price"),
                "desc": request.form.get("desc"),
                "img": request.form.get("img")
            }
            save_config(config_data)
            global ROOM_TYPES
            ROOM_TYPES = config_data["ROOM_TYPES"]
            flash("Room updated successfully!", "success")
    except Exception as e:
        flash(f"Error updating room: {str(e)}", "error")
    
    return redirect(url_for('admin_rooms'))

@app.route("/admin/room/delete/<int:index>", methods=["POST"])
@login_required
def admin_room_delete(index):
    try:
        config_data = load_config()
        if 0 <= index < len(config_data["ROOM_TYPES"]):
            del config_data["ROOM_TYPES"][index]
            save_config(config_data)
            global ROOM_TYPES
            ROOM_TYPES = config_data["ROOM_TYPES"]
            flash("Room deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting room: {str(e)}", "error")
    
    return redirect(url_for('admin_rooms'))

# ===== SPECIALITIES MANAGEMENT =====

@app.route("/admin/specialities")
@login_required
def admin_specialities():
    config_data = load_config()
    cafe_spec = config_data.get("CAFE_SPECIALITIES", [])
    homestay_spec = config_data.get("HOMESTAY_SPECIALITIES", [])
    return render_template("admin/specialities.html", cafe_spec=cafe_spec, homestay_spec=homestay_spec, site=SITE)

@app.route("/admin/speciality/add", methods=["POST"])
@login_required
def admin_speciality_add():
    try:
        config_data = load_config()
        spec_type = request.form.get("spec_type")
        icon = request.form.get("icon")
        title = request.form.get("title")
        desc = request.form.get("desc")
        
        new_spec = {
            "icon": icon,
            "title": title,
            "desc": desc
        }
        
        if spec_type == "cafe":
            config_data["CAFE_SPECIALITIES"].append(new_spec)
            global CAFE_SPECIALITIES
            CAFE_SPECIALITIES = config_data["CAFE_SPECIALITIES"]
        else:
            config_data["HOMESTAY_SPECIALITIES"].append(new_spec)
            global HOMESTAY_SPECIALITIES
            HOMESTAY_SPECIALITIES = config_data["HOMESTAY_SPECIALITIES"]
        
        save_config(config_data)
        flash("Speciality added successfully!", "success")
    except Exception as e:
        flash(f"Error adding speciality: {str(e)}", "error")
    
    return redirect(url_for('admin_specialities'))

@app.route("/admin/speciality/delete/<spec_type>/<int:index>", methods=["POST"])
@login_required
def admin_speciality_delete(spec_type, index):
    try:
        config_data = load_config()
        
        if spec_type == "cafe":
            if 0 <= index < len(config_data["CAFE_SPECIALITIES"]):
                del config_data["CAFE_SPECIALITIES"][index]
                global CAFE_SPECIALITIES
                CAFE_SPECIALITIES = config_data["CAFE_SPECIALITIES"]
        else:
            if 0 <= index < len(config_data["HOMESTAY_SPECIALITIES"]):
                del config_data["HOMESTAY_SPECIALITIES"][index]
                global HOMESTAY_SPECIALITIES
                HOMESTAY_SPECIALITIES = config_data["HOMESTAY_SPECIALITIES"]
        
        save_config(config_data)
        flash("Speciality deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting speciality: {str(e)}", "error")
    
    return redirect(url_for('admin_specialities'))

# ===== SITE SETTINGS =====

@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def admin_settings():
    if request.method == "POST":
        try:
            config_data = load_config()
            
            # Update SITE settings
            config_data["SITE"] = {
                "phone": request.form.get("phone"),
                "whatsapp": request.form.get("whatsapp"),
                "email": request.form.get("email"),
                "address": request.form.get("address"),
                "google_rating_cafe": float(request.form.get("google_rating_cafe")),
                "google_reviews_cafe": int(request.form.get("google_reviews_cafe")),
                "google_rating_homestay": float(request.form.get("google_rating_homestay")),
                "google_reviews_homestay": int(request.form.get("google_reviews_homestay")),
                "maps_link_cafe": request.form.get("maps_link_cafe"),
                "maps_link_homestay": request.form.get("maps_link_homestay")
            }
            
            # Update MAIL_API
            config_data["MAIL_API"] = {
                "api_key": request.form.get("api_key"),
                "api_url": request.form.get("api_url"),
                "from_email": request.form.get("from_email"),
                "to_email": request.form.get("to_email")
            }
            
            save_config(config_data)
            
            # Reload global variables
            global SITE
            SITE = config_data["SITE"]
            
            flash("Settings updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating settings: {str(e)}", "error")
        
        return redirect(url_for('admin_settings'))
    
    config_data = load_config()
    return render_template("admin/settings.html", site=SITE, mail_api=config_data.get("MAIL_API", {}), config=config_data)

@app.route("/admin/config")
@login_required
def admin_config():
    config_data = load_config()
    return render_template("admin/config.html", config=config_data)

@app.route("/admin/update", methods=["POST"])
@login_required
def admin_update():
    try:
        new_config = request.get_json()
        save_config(new_config)
        
        # Reload config globally
        global config, SITE, CAFE_REVIEWS, HOMESTAY_REVIEWS, CAFE_MENU
        global ROOM_TYPES, CAFE_LOCAL_FOOD, CAFE_SPECIALITIES, HOMESTAY_SPECIALITIES
        global MOUNTAIN_VIEW_INFO, KINNAUR_LOCAL_SPECIALITIES, BLOG_POSTS
        
        config = load_config()
        SITE = config["SITE"]
        CAFE_REVIEWS = config["CAFE_REVIEWS"]
        HOMESTAY_REVIEWS = config["HOMESTAY_REVIEWS"]
        CAFE_MENU = config["CAFE_MENU"]
        ROOM_TYPES = config["ROOM_TYPES"]
        CAFE_LOCAL_FOOD = config["CAFE_LOCAL_FOOD"]
        CAFE_SPECIALITIES = config["CAFE_SPECIALITIES"]
        HOMESTAY_SPECIALITIES = config["HOMESTAY_SPECIALITIES"]
        MOUNTAIN_VIEW_INFO = config["MOUNTAIN_VIEW_INFO"]
        KINNAUR_LOCAL_SPECIALITIES = config["KINNAUR_LOCAL_SPECIALITIES"]
        BLOG_POSTS = config["BLOG_POSTS"]
        
        return jsonify({"success": True, "message": "Configuration updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)