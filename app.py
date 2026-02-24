from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os

app = Flask(__name__)

# -------------------------
# DATABASE SETUP
# -------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE URL FOUND:", DATABASE_URL is not None)

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    print("⚠️ FALLING BACK TO SQLITE")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beer.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# -------------------------
# MODEL
# -------------------------
class Special(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bar_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200))
    deal = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------
# GEOCODING
# -------------------------
def geocode(bar, address=None):
    try:
        query = f"{bar}, {address}" if address else bar
        url = "https://nominatim.openstreetmap.org/search"

        params = {"q": query, "format": "json", "limit": 1}
        headers = {"User-Agent": "BeerDollarsApp"}

        r = requests.get(url, params=params, headers=headers, timeout=6)
        data = r.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])

    except Exception as e:
        print("Geocode error:", e)

    return None, None


# -------------------------
# SEED DATA
# -------------------------
def seed_data():
    if Special.query.count() > 0:
        return

    starters = [
        ("La Villa Tavern", "Struthers Ohio", "$2 bottles", "Monday"),
        ("Los Gallos", "Boardman Ohio", "$2 bottles", "Monday"),
        ("John & Helen’s Tavern", "Kensington Ohio", "$2.50 bottles", "Wednesday"),
    ]

    for bar, addr, deal, day in starters:
        lat, lon = geocode(bar, addr)

        db.session.add(Special(
            bar_name=bar,
            address=addr,
            deal=deal,
            day=day.strip().capitalize(),
            latitude=lat,
            longitude=lon,
            verified=True
        ))

    db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add_special", methods=["POST"])
def add_special():
    try:
        data = request.json

        print("INCOMING DATA:", data)

        day_clean = data.get("day", "").strip().capitalize()

        lat, lon = geocode(
            data.get("bar_name"),
            data.get("address")
        )

        new_special = Special(
            bar_name=data.get("bar_name"),
            address=data.get("address"),
            deal=data.get("deal"),
            day=day_clean,
            latitude=lat,
            longitude=lon
        )

        db.session.add(new_special)
        db.session.commit()

        print("SAVED:", new_special.bar_name)

        return jsonify({"status": "Saved Successfully"})

    except Exception as e:
        print("SAVE ERROR:", e)
        db.session.rollback()
        return jsonify({"status": "Error saving"}), 500


@app.route("/get_specials/<day>")
def get_specials(day):
    day_clean = day.strip().capitalize()

    specials = Special.query.filter_by(day=day_clean).all()

    print(f"FETCHING SPECIALS FOR: {day_clean} → {len(specials)} found")

    return jsonify([
        {
            "bar_name": s.bar_name,
            "address": s.address,
            "deal": s.deal,
            "verified": s.verified,
            "latitude": s.latitude,
            "longitude": s.longitude,
        }
        for s in specials
    ])


if __name__ == "__main__":
    app.run(debug=True)
