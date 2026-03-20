from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import random
import math
import os
from twilio.rest import Client as TwilioClient
import googlemaps

from config import Config
from models import db, User, VerificationCode, Bar

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

gmaps = googlemaps.Client(key=app.config["GOOGLE_MAPS_API_KEY"])

# Set a Master Bypass Code for testing
MASTER_BYPASS_CODE = "0000"

with app.app_context():
    db.create_all()

# ---------- Helpers ----------
def generate_code():
    return f"{random.randint(0, 9999):04d}"

def haversine_distance(lat1, lng1, lat2, lng2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def normalize_day(day_str):
    return day_str.strip().lower()

def geocode_address(address):
    try:
        result = gmaps.geocode(address)
        if not result:
            raise ValueError("Address not found")
        loc = result[0]['geometry']['location']
        return loc['lat'], loc['lng']
    except Exception as e:
        raise ValueError(f"Geocoding failed: {str(e)}")

def send_sms(phone, code):
    # FORCE PRINT TO LOGS: This ensures you see the code in Render regardless of Twilio
    print(f"\n[!!! DEBUG !!!] VERIFICATION CODE FOR {phone} IS: {code}\n")
    
    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_from = os.environ.get("TWILIO_PHONE_NUMBER")
    
    if twilio_sid and twilio_token and twilio_from:
        try:
            client = TwilioClient(twilio_sid, twilio_token)
            client.messages.create(
                body=f"Your Beer Dollars code is: {code}",
                from_=twilio_from,
                to=phone
            )
            print(f"[SMS] Twilio attempt successful for {phone}")
        except Exception as e:
            print(f"[SMS ERROR] Twilio failed: {e}")
    else:
        print(f"[SMS INFO] Twilio credentials missing. Use the DEBUG code printed above.")

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])

@app.route("/login")
@app.route("/main")
def main_page():
    return render_template("main.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])

@app.route("/api/session_status")
def session_status():
    return jsonify({
        "verified": session.get("verified", False),
        "phone": session.get("phone", None)
    })

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
    
    send_sms(phone, code)
    return jsonify({"success": True})

@app.route("/api/verify_code", methods=["POST"])
def verify_code():
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    code = data.get("code", "").strip()

    # --- CIRCUMVENT LOGIC (Master Bypass) ---
    if code == MASTER_BYPASS_CODE:
        print(f"[AUTH] Master Bypass used for {phone}")
        is_valid = True
    else:
        vc = VerificationCode.query.filter_by(phone=phone, code=code).order_by(VerificationCode.created_at.desc()).first()
        is_valid = vc is not None

    if not is_valid:
        return jsonify({"success": False, "error": "Invalid code"}), 400

    # User handling
    user = User.query.filter_by(phone=phone).first() or User(phone=phone, terms_accepted=True)
    user.last_login = datetime.utcnow()
    db.session.add(user)
    db.session.commit()
    
    session["phone"] = phone
    session["verified"] = True
    return jsonify({"success": True})

# --- Keeping the rest of your original API routes ---
@app.route("/api/bars", methods=["GET"])
def get_bars():
    day = normalize_day(request.args.get("day", ""))
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=35.0, type=float)
    query = Bar.query
    if day:
        query = query.filter_by(day_of_week=day)
    bars = query.all()
    result = []
    for b in bars:
        dist = haversine_distance(lat, lng, b.lat, b.lng) if lat and lng else None
        if dist is None or dist <= radius:
            result.append({
                "id": b.id, "name": b.name, "address": b.address,
                "deal": b.deal, "day_of_week": b.day_of_week,
                "lat": b.lat, "lng": b.lng,
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
    if not all([name, address, deal, day]):
        return jsonify({"success": False, "error": "Missing fields"}), 400
    
    try:
        lat, lng = geocode_address(address)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
        
    bar = Bar(name=name, address=address, deal=deal, day_of_week=day, lat=lat, lng=lng)
    db.session.add(bar)
    db.session.commit()
    return jsonify({"success": True, "bar_id": bar.id})

if __name__ == "__main__":
    app.run(debug=True)
    
