from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import random
import math
import googlemaps  # <-- NEW

from config import Config
from models import db, User, VerificationCode, Bar

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Google Maps client (server-side geocoding)
gmaps = googlemaps.Client(key=app.config["GOOGLE_MAPS_API_KEY"])

with app.app_context():
    db.create_all()

# ---------- Helpers ----------
def generate_code():
    return f"{random.randint(0, 9999):04d}"

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 3958.8  # Earth radius in miles
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def normalize_day(day_str):
    return day_str.strip().lower()

def geocode_address(address):
    """Returns (lat, lng) or raises exception"""
    try:
        result = gmaps.geocode(address)
        if not result:
            raise ValueError("Address not found")
        location = result[0]['geometry']['location']
        return location['lat'], location['lng']
    except Exception as e:
        raise ValueError(f"Geocoding failed: {str(e)}")

# ---------- Routes ----------
@app.route("/")
def index():
    # This is your splash/loading screen entry point
    # Put your big BEER DOLLARS logo + loading bar in index.html
    return render_template("index.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])

@app.route("/admin")
def admin():
    return render_template("admin.html")

# --- Auth ---
@app.route("/api/send_code", methods=["POST"])
def send_code():
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    if not phone:
        return jsonify({"success": False, "error": "Phone required"}), 400

    code = generate_code()
    vc = VerificationCode(phone=phone, code=code)
    db.session.add(vc)
    db.session.commit()

    print(f"[DEBUG] CODE for {phone}: {code}")  # Replace with Twilio later
    return jsonify({"success": True})

@app.route("/api/verify_code", methods=["POST"])
def verify_code():
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    code = data.get("code", "").strip()

    vc = VerificationCode.query.filter_by(phone=phone, code=code).order_by(VerificationCode.created_at.desc()).first()
    if not vc:
        return jsonify({"success": False, "error": "Invalid code"}), 400

    user = User.query.filter_by(phone=phone).first() or User(phone=phone, terms_accepted=True)
    user.last_login = datetime.utcnow()
    db.session.add(user)
    db.session.commit()

    session["phone"] = phone
    session["verified"] = True
    return jsonify({"success": True})

# --- Bars ---
@app.route("/api/bars", methods=["GET"])
def get_bars():
    day = normalize_day(request.args.get("day", ""))
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=35.0, type=float)  # Your 35-mile default

    query = Bar.query
    if day:
        query = query.filter_by(day_of_week=day)

    bars = query.all()
    result = []

    for b in bars:
        dist = haversine_distance(lat, lng, b.lat, b.lng) if lat and lng else None
        if dist is None or dist <= radius:
            result.append({
                "id": b.id,
                "name": b.name,
                "address": b.address,
                "deal": b.deal,           # Drinks only!
                "day_of_week": b.day_of_week,
                "lat": b.lat,
                "lng": b.lng,
                "distance": round(dist, 1) if dist else None
            })

    result.sort(key=lambda x: x["distance"] if x["distance"] is not None else 999999)
    return jsonify({"success": True, "bars": result})

@app.route("/api/bars", methods=["POST"])
def add_bar():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    address = data.get("address", "").strip()
    deal = data.get("deal", "").strip()
    day = normalize_day(data.get("day_of_week", ""))

    # DRINKS ONLY enforcement (you can make this stricter later)
    if not all([name, address, deal, day]):
        return jsonify({"success": False, "error": "Name, address, deal, and day required"}), 400

    # NEW: Auto-geocode if lat/lng not provided (this fixes your Denny's Blue Angel issue)
    lat = data.get("lat")
    lng = data.get("lng")
    if lat is None or lng is None:
        try:
            lat, lng = geocode_address(address)
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

    bar = Bar(
        name=name,
        address=address,
        deal=deal,
        day_of_week=day,
        lat=lat,
        lng=lng
    )
    db.session.add(bar)
    db.session.commit()

    return jsonify({"success": True, "bar_id": bar.id, "lat": lat, "lng": lng})

@app.route("/api/admin/bars")
def admin_bars():
    bars = Bar.query.order_by(Bar.created_at.desc()).all()
    return jsonify({"success": True, "bars": [b.__dict__ for b in bars if not "_sa_instance_state" in b.__dict__]})

if __name__ == "__main__":
    app.run(debug=True)
