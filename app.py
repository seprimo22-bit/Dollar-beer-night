
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import random
import math
import os
import googlemaps

from config import Config
from models import db, User, VerificationCode, Bar

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

gmaps = googlemaps.Client(key=app.config["GOOGLE_MAPS_API_KEY"])

with app.app_context():
    db.create_all()

# ---------- Auto-generate main.html if missing ----------
MAIN_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Beer Dollars</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a1628; color: #fff; overflow: hidden; }
    .hidden { display: none !important; }
    .screen { position: fixed; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 24px; }

    /* LOADING */
    #screen-loading { background: linear-gradient(160deg, #0a1628 0%, #001a4d 60%, #0a1628 100%); gap: 24px; }
    .loading-logo { width: min(280px, 75vw); height: auto; filter: drop-shadow(0 0 24px rgba(30,144,255,0.5)); animation: pulse 2s ease-in-out infinite; }
    @keyframes pulse { 0%,100% { filter: drop-shadow(0 0 24px rgba(30,144,255,0.4)); } 50% { filter: drop-shadow(0 0 40px rgba(30,144,255,0.8)); } }
    .loading-tagline { font-size: 1.1rem; font-style: italic; color: rgba(255,255,255,0.8); }
    .loading-bar-track { width: min(320px,80vw); height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }
    #beer-fill { height: 100%; width: 0%; background: linear-gradient(90deg,#1e90ff,#00bfff); border-radius: 4px; transition: width 0.9s ease-in-out; }
    .loading-footer { position: fixed; bottom: 24px; font-size: 0.75rem; color: rgba(255,255,255,0.4); text-align: center; line-height: 1.6; }

    /* AUTH */
    #screen-phone, #screen-code { background: linear-gradient(160deg,#0a1628 0%,#001a4d 100%); gap: 0; }
    .auth-card { width: 100%; max-width: 400px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 36px 28px; display: flex; flex-direction: column; gap: 20px; }
    .auth-logo-small { width: 72px; height: 72px; object-fit: contain; margin: 0 auto 4px; }
    .auth-title { font-size: 1.5rem; font-weight: 700; text-align: center; }
    .auth-subtitle { font-size: 0.9rem; color: rgba(255,255,255,0.55); text-align: center; line-height: 1.5; }
    .auth-label { font-size: 0.8rem; font-weight: 600; color: rgba(255,255,255,0.6); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
    .auth-input { width: 100%; padding: 14px 16px; background: rgba(255,255,255,0.08); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 12px; color: #fff; font-size: 1.1rem; outline: none; -webkit-appearance: none; }
    .auth-input:focus { border-color: #1e90ff; background: rgba(30,144,255,0.08); }
    .auth-input::placeholder { color: rgba(255,255,255,0.3); }
    .auth-btn { width: 100%; padding: 15px; background: linear-gradient(135deg,#1e6fff,#1e90ff); border: none; border-radius: 12px; color: #fff; font-size: 1rem; font-weight: 700; cursor: pointer; -webkit-tap-highlight-color: transparent; }
    .auth-btn:active { opacity: 0.85; }
    .auth-error { font-size: 0.85rem; color: #ff6b6b; text-align: center; min-height: 18px; }
    .auth-link { font-size: 0.85rem; color: rgba(255,255,255,0.45); text-align: center; }
    .auth-link span { color: #1e90ff; cursor: pointer; text-decoration: underline; }
    .code-inputs { display: flex; gap: 12px; justify-content: center; }
    .code-digit { width: 58px; height: 64px; background: rgba(255,255,255,0.08); border: 1.5px solid rgba(255,255,255,0.15); border-radius: 12px; color: #fff; font-size: 1.8rem; font-weight: 700; text-align: center; outline: none; -webkit-appearance: none; }
    .code-digit:focus { border-color: #1e90ff; }

    /* MAIN */
    #screen-main { display: flex; flex-direction: column; justify-content: flex-start; align-items: stretch; padding: 0; background: #0f1b2d; overflow: hidden; }
    .app-header { background: linear-gradient(135deg,#1456cc,#1e90ff); padding: 16px 16px 12px; flex-shrink: 0; }
    .header-top { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
    .header-logo { width: 32px; height: 32px; object-fit: contain; }
    .header-title { font-size: 1.3rem; font-weight: 800; flex: 1; }
    .search-bar { display: flex; align-items: center; background: rgba(255,255,255,0.18); border-radius: 10px; padding: 10px 14px; gap: 8px; }
    #search-input { background: none; border: none; outline: none; color: #fff; font-size: 0.95rem; width: 100%; }
    #search-input::placeholder { color: rgba(255,255,255,0.55); }
    .day-selector-wrap { background: #0f1b2d; padding: 10px 12px; flex-shrink: 0; border-bottom: 1px solid rgba(255,255,255,0.06); }
    #day-selector { display: flex; gap: 6px; overflow-x: auto; scrollbar-width: none; padding-bottom: 2px; }
    #day-selector::-webkit-scrollbar { display: none; }
    .day-pill { flex-shrink: 0; padding: 7px 14px; background: rgba(255,255,255,0.07); border: 1.5px solid rgba(255,255,255,0.1); border-radius: 20px; color: rgba(255,255,255,0.6); font-size: 0.8rem; font-weight: 600; cursor: pointer; -webkit-tap-highlight-color: transparent; }
    .day-pill.active { background: #1e90ff; border-color: #1e90ff; color: #fff; }
    #day-message { padding: 8px 16px; font-size: 0.8rem; color: rgba(255,255,255,0.4); font-style: italic; flex-shrink: 0; }
    .location-bar { display: flex; align-items: center; gap: 8px; padding: 10px 16px; background: rgba(255,255,255,0.04); border-bottom: 1px solid rgba(255,255,255,0.06); flex-shrink: 0; }
    #location-input { flex: 1; background: none; border: none; outline: none; color: rgba(255,255,255,0.7); font-size: 0.85rem; }
    #location-input::placeholder { color: rgba(255,255,255,0.3); }
    #use-location-btn { background: rgba(30,144,255,0.2); border: 1px solid rgba(30,144,255,0.4); border-radius: 8px; color: #4fc3f7; font-size: 0.75rem; font-weight: 600; padding: 6px 10px; cursor: pointer; white-space: nowrap; }
    .app-content { flex: 1; overflow-y: auto; -webkit-overflow-scrolling: touch; display: flex; flex-direction: column; }
    #bar-list { flex-shrink: 0; display: flex; flex-direction: column; gap: 1px; background: rgba(255,255,255,0.05); }
    .bar-card { background: #131f33; padding: 14px 16px; display: flex; align-items: center; gap: 14px; cursor: pointer; -webkit-tap-highlight-color: transparent; }
    .bar-card.active, .bar-card:active { background: #1a2d4a; }
    .bar-icon { font-size: 1.6rem; flex-shrink: 0; width: 40px; text-align: center; }
    .bar-info { flex: 1; min-width: 0; }
    .bar-name { font-size: 0.95rem; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #fff; }
    .bar-deal { font-size: 0.9rem; color: #4fc3f7; font-weight: 600; margin: 2px 0; }
    .bar-meta { font-size: 0.75rem; color: rgba(255,255,255,0.4); }
    .bar-distance { font-size: 0.8rem; color: rgba(255,255,255,0.4); flex-shrink: 0; }
    .bar-list-empty { padding: 40px 24px; text-align: center; color: rgba(255,255,255,0.3); font-size: 0.9rem; line-height: 1.6; }
    #map { height: 240px; flex-shrink: 0; background: #0d1929; }
    .fab { position: fixed; bottom: 24px; right: 20px; width: 56px; height: 56px; background: linear-gradient(135deg,#1e6fff,#1e90ff); border: none; border-radius: 50%; color: #fff; font-size: 1.5rem; cursor: pointer; box-shadow: 0 4px 20px rgba(30,144,255,0.5); display: flex; align-items: center; justify-content: center; z-index: 100; -webkit-tap-highlight-color: transparent; }
    .fab:active { transform: scale(0.93); }
  </style>
</head>
<body>

  <!-- LOADING -->
  <div id="screen-loading" class="screen">
    <img src="{{ url_for('static', filename='images/beer-dollars-logo.png') }}" alt="Beer Dollars" class="loading-logo" />
    <div class="loading-tagline">"STRETCH YOUR BEER MONEY"</div>
    <div class="loading-bar-track"><div id="beer-fill"></div></div>
    <div class="loading-footer">Crafted for Beer Lovers &bull; Est. 2024<br/>Follow us: @beer_dollars_app</div>
  </div>

  <!-- PHONE -->
  <div id="screen-phone" class="screen hidden">
    <div class="auth-card">
      <img src="{{ url_for('static', filename='images/beer-dollars-logo.png') }}" alt="" class="auth-logo-small" onerror="this.style.display='none'" />
      <div class="auth-title">🍺 Beer Dollars</div>
      <div class="auth-subtitle">Enter your phone number to find cheap beers near you.</div>
      <div>
        <div class="auth-label">Phone Number</div>
        <input id="phone-input" class="auth-input" type="tel" placeholder="+1 (555) 000-0000" inputmode="tel" autocomplete="tel" />
      </div>
      <div id="phone-error" class="auth-error"></div>
      <button id="send-code-btn" class="auth-btn">Send Code →</button>
      <div class="auth-link">We will text you a 4-digit code. No spam, ever.</div>
    </div>
  </div>

  <!-- CODE -->
  <div id="screen-code" class="screen hidden">
    <div class="auth-card">
      <div style="font-size:2.5rem;text-align:center;">📱</div>
      <div class="auth-title">Check your texts</div>
      <div class="auth-subtitle">We sent a 4-digit code to your phone.</div>
      <div class="code-inputs">
        <input class="code-digit" id="digit-0" type="tel" maxlength="1" inputmode="numeric" />
        <input class="code-digit" id="digit-1" type="tel" maxlength="1" inputmode="numeric" />
        <input class="code-digit" id="digit-2" type="tel" maxlength="1" inputmode="numeric" />
        <input class="code-digit" id="digit-3" type="tel" maxlength="1" inputmode="numeric" />
      </div>
      <input id="code-input" type="hidden" />
      <div id="code-error" class="auth-error"></div>
      <button id="verify-code-btn" class="auth-btn">Verify →</button>
      <div class="auth-link">Didn\'t get it? <span id="resend-code-btn">Resend code</span></div>
    </div>
  </div>

  <!-- MAIN -->
  <div id="screen-main" class="screen hidden" style="justify-content:flex-start;">
    <div class="app-header">
      <div class="header-top">
        <img src="{{ url_for('static', filename='images/beer-dollars-logo.png') }}" alt="" class="header-logo" onerror="this.style.display=\'none\'" />
        <div class="header-title">Beer Dollars 🍺</div>
      </div>
      <div class="search-bar">
        <span>🔍</span>
        <input id="search-input" type="search" placeholder="Search bars or specials…" autocomplete="off" />
      </div>
    </div>
    <div class="day-selector-wrap"><div id="day-selector"></div></div>
    <div id="day-message"></div>
    <div class="location-bar">
      <span>📍</span>
      <input id="location-input" type="text" placeholder="Enter city or zip…" />
      <button id="use-location-btn">Use My Location</button>
    </div>
    <div class="app-content">
      <div id="bar-list">
        <div class="bar-list-empty">📍 Allow location or enter a city above to find cheap beers near you.</div>
      </div>
      <div id="map"></div>
    </div>
    <button class="fab" id="add-special-btn">＋</button>
  </div>

  <script src="{{ url_for('static', filename='app.js') }}"></script>
  <script src="https://maps.googleapis.com/maps/api/js?key={{ google_maps_api_key }}&callback=initMap" async defer></script>
  <script src="{{ url_for('static', filename='map.js') }}"></script>
  <script>
    (function() {
      var digits = [\'digit-0\',\'digit-1\',\'digit-2\',\'digit-3\'];
      digits.forEach(function(id, i) {
        var el = document.getElementById(id);
        if (!el) return;
        el.addEventListener(\'input\', function() {
          el.value = el.value.replace(/\\D/g,\'\').slice(0,1);
          var combined = digits.map(function(d){ return document.getElementById(d).value; }).join(\'\');
          document.getElementById(\'code-input\').value = combined;
          if (el.value && i < digits.length - 1) document.getElementById(digits[i+1]).focus();
          if (combined.length === 4) document.getElementById(\'verify-code-btn\').click();
        });
        el.addEventListener(\'keydown\', function(e) {
          if (e.key === \'Backspace\' && !el.value && i > 0) document.getElementById(digits[i-1]).focus();
        });
      });
    })();
  </script>
</body>
</html>'''

# Write main.html to templates folder if it doesn't exist
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
main_html_path = os.path.join(templates_dir, 'main.html')
if not os.path.exists(main_html_path):
    with open(main_html_path, 'w') as f:
        f.write(MAIN_HTML)
    print("[INFO] main.html created in templates/")

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

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("index.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])

@app.route("/login")
@app.route("/main")
def main():
    return render_template("main.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])

@app.route("/api/session_status")
def session_status():
    return jsonify({
        "verified": session.get("verified", False),
        "phone": session.get("phone", None)
    })

@app.route("/admin")
def admin():
    return render_template("admin.html")

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
    print(f"[DEBUG] CODE for {phone}: {code}")
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
        return jsonify({"success": False, "error": "Name, address, deal, and day required"}), 400
    lat = data.get("lat")
    lng = data.get("lng")
    if lat is None or lng is None:
        try:
            lat, lng = geocode_address(address)
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400
    bar = Bar(name=name, address=address, deal=deal, day_of_week=day, lat=lat, lng=lng)
    db.session.add(bar)
    db.session.commit()
    return jsonify({"success": True, "bar_id": bar.id, "lat": lat, "lng": lng})

@app.route("/api/admin/bars")
def admin_bars():
    bars = Bar.query.order_by(Bar.created_at.desc()).all()
    return jsonify({"success": True, "bars": [
        {k: v for k, v in b.__dict__.items() if k != "_sa_instance_state"}
        for b in bars
    ]})

if __name__ == "__main__":
    app.run(debug=True)

