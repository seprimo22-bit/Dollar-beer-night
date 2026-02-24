from flask import Flask, render_template, request, jsonify, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os

# ---------- APP SETUP ----------
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = os.getenv("SECRET_KEY", "brick_secret_2026")

# ---------- DATABASE ----------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL or "sqlite:///beer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------- MODEL ----------
class Special(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bar_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200))
    deal = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ---------- INIT DATABASE ----------
with app.app_context():
    db.create_all()

# ---------- CONFIG ----------
ADMIN_KEY = os.getenv("ADMIN_KEY", "BeerBoss2026!")

# ---------- UTILITIES ----------
def normalize(text):
    return text.lower().replace("'", "").replace("’", "").strip()

def contains_food(deal):
    banned = ["wings", "pizza", "burger", "fries", "food", "sandwich"]
    return any(word in deal.lower() for word in banned)

def geocode(bar, address=None):
    try:
        query = f"{bar}, {address}" if address else bar

        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": "BeerDollarsApp"},
            timeout=8
        )

        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print("Geocode error:", e)

    return None, None

def is_duplicate(day, deal, bar_name):
    specials = Special.query.filter_by(day=day).all()
    bar_norm = normalize(bar_name)
    deal_norm = normalize(deal)

    for s in specials:
        if normalize(s.bar_name) == bar_norm and normalize(s.deal) == deal_norm:
            return True
    return False

# ---------- ROUTES ----------

@app.route("/")
def home():
    return render_template("index.html", admin=session.get("admin"))

# ---------- ADMIN LOGIN ----------
@app.route("/admin")
def admin_login():
    key = request.args.get("key")
    if key == ADMIN_KEY:
        session["admin"] = True
    return redirect("/admin-panel")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- ADMIN PANEL ----------
@app.route("/admin-panel")
def admin_panel():
    if not session.get("admin"):
        return "Unauthorized", 403

    specials = Special.query.order_by(Special.day, Special.bar_name).all()
    return render_template("admin.html", specials=specials)

# ---------- ADD SPECIAL ----------
@app.route("/add_special", methods=["POST"])
def add_special():
    try:
        data = request.json

        bar_name = data.get("bar_name", "").strip()
        address = data.get("address", "").strip()
        deal = data.get("deal", "").strip()
        day_clean = data.get("day", "").strip().capitalize()

        if not bar_name or not deal or not day_clean:
            return jsonify(success=False, message="Missing info")

        if contains_food(deal):
            return jsonify(success=False, message="Food specials not allowed")

        if is_duplicate(day_clean, deal, bar_name):
            return jsonify(success=False, message="Duplicate")

        lat, lon = geocode(bar_name, address)

        special = Special(
            bar_name=bar_name,
            address=address,
            deal=deal,
            day=day_clean,
            latitude=lat,
            longitude=lon
        )

        db.session.add(special)
        db.session.commit()

        return jsonify(success=True)

    except Exception as e:
        print("SAVE ERROR:", e)
        db.session.rollback()
        return jsonify(success=False), 500

# ---------- GET SPECIALS ----------
@app.route("/get_specials/<day>")
def get_specials(day):
    day_clean = day.strip().capitalize()
    specials = Special.query.filter_by(day=day_clean).all()

    return jsonify([
        dict(
            id=s.id,
            bar_name=s.bar_name,
            address=s.address,
            deal=s.deal,
            latitude=s.latitude,
            longitude=s.longitude
        )
        for s in specials
    ])

# ---------- EDIT SPECIAL ----------
@app.route("/edit_special/<int:id>", methods=["POST"])
def edit_special(id):
    if not session.get("admin"):
        return "Unauthorized", 403

    special = Special.query.get_or_404(id)

    bar_name = request.form.get("bar_name")
    address = request.form.get("address")
    deal = request.form.get("deal")
    day = request.form.get("day")

    special.bar_name = bar_name
    special.address = address
    special.deal = deal
    special.day = day.capitalize()

    lat, lon = geocode(bar_name, address)
    special.latitude = lat
    special.longitude = lon

    db.session.commit()
    return redirect("/admin-panel")

# ---------- DELETE SPECIAL ----------
@app.route("/delete_special/<int:id>", methods=["POST"])
def delete_special(id):
    if not session.get("admin"):
        return "Unauthorized", 403

    special = Special.query.get_or_404(id)
    db.session.delete(special)
    db.session.commit()

    return redirect("/admin-panel")
