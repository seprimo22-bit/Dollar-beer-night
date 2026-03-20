from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import random
import math

from config import Config
from models import db, User, VerificationCode, Bar

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

# ---------- Helpers ----------

def generate_code():
    return f"{random.randint(0, 9999):04d}"

def haversine_distance(lat1, lng1, lat2, lng2):
    # distance in miles
    R = 3958.8
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def normalize_day(day_str):
    return day_str.strip().lower()

# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])

@app.route("/admin")
def admin():
    return render_template("admin.html")

# --- Auth / Verification ---

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

    # In production: send SMS here.
    # For now, we just log it so you can see it in logs.
    print(f"[DEBUG] Verification code for {phone}: {code}")

    return jsonify({"success": True})

@app.route("/api/verify_code", methods=["POST"])
def verify_code():
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    code = data.get("code", "").strip()

    if not phone or not code:
        return jsonify({"success": False, "error": "Phone and code required"}), 400

    vc = (
        VerificationCode.query
        .filter_by(phone=phone, code=code)
        .order_by(VerificationCode.created_at.desc())
        .first()
    )
    if not vc:
        return jsonify({"success": False, "error": "Invalid code"}), 400

    user = User.query.filter_by(phone=phone).first()
    now = datetime.utcnow()
    if not user:
        user = User(phone=phone, created_at=now, last_login=now, terms_accepted=True)
        db.session.add(user)
    else:
        user.last_login = now

    db.session.commit()

    session["phone"] = phone
    session["verified"] = True

    return jsonify({"success": True})

@app.route("/api/session_status")
def session_status():
    return jsonify({
        "verified": bool(session.get("verified")),
        "phone": session.get("phone")
    })

# --- Bars API ---

@app.route("/api/bars", methods=["GET"])
def get_bars():
    day = normalize_day(request.args.get("day", ""))
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=45.0, type=float)

    query = Bar.query
    if day:
        query = query.filter_by(day_of_week=day)

    bars = query.all()
    result = []

    for b in bars:
        if lat is not None and lng is not None:
            dist = haversine_distance(lat, lng, b.lat, b.lng)
            if dist > radius:
                continue
        else:
            dist = None

        result.append({
            "id": b.id,
            "name": b.name,
            "address": b.address,
            "city": b.city,
            "state": b.state,
            "zip_code": b.zip_code,
            "deal": b.deal,
            "day_of_week": b.day_of_week,
            "lat": b.lat,
            "lng": b.lng,
            "distance": dist
        })

    # sort by distance if available
    result.sort(key=lambda x: x["distance"] if x["distance"] is not None else 999999)

    return jsonify({"success": True, "bars": result})

@app.route("/api/bars", methods=["POST"])
def add_bar():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    address = data.get("address", "").strip()
    deal = data.get("deal", "").strip()
    day = normalize_day(data.get("day_of_week", ""))
    lat = data.get("lat", None)
    lng = data.get("lng", None)
    city = data.get("city", "").strip()
    state = data.get("state", "").strip()
    zip_code = data.get("zip_code", "").strip()

    if not all([name, address, deal, day]) or lat is None or lng is None:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    bar = Bar(
        name=name,
        address=address,
        deal=deal,
        day_of_week=day,
        lat=lat,
        lng=lng,
        city=city,
        state=state,
        zip_code=zip_code
    )
    db.session.add(bar)
    db.session.commit()

    return jsonify({"success": True, "bar_id": bar.id})

# --- Simple admin list ---

@app.route("/api/admin/bars")
def admin_bars():
    bars = Bar.query.order_by(Bar.created_at.desc()).all()
    result = []
    for b in bars:
        result.append({
            "id": b.id,
            "name": b.name,
            "address": b.address,
            "deal": b.deal,
            "day_of_week": b.day_of_week,
            "lat": b.lat,
            "lng": b.lng,
            "city": b.city,
            "state": b.state,
            "zip_code": b.zip_code
        })
    return jsonify({"success": True, "bars": result})

if __name__ == "__main__":
    app.run(debug=True)
