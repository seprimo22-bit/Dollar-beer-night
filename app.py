from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------------
# DATABASE MODEL
# ----------------------
class Special(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bar_name = db.Column(db.String(120), nullable=False)
    deal = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ----------------------
# GEOCODING FUNCTION
# ----------------------
def geocode_location(query):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "BeerDollarsApp"
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)
        data = response.json()

        if len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print("Geocode error:", e)

    return None, None


# ----------------------
# SEED DATA
# ----------------------
def seed_data():

    existing = Special.query.all()
    if len(existing) > 0:
        return

    seed_list = [

        # Existing verified bars
        ("Lanai Lounge, Boardman Ohio", "$1.50 cans", "Sunday"),
        ("Steel City Bar & Grill, Youngstown Ohio", "$2 bottles (2–8 PM)", "Saturday"),
        ("John & Helen’s Tavern, Kensington Ohio", "$2.50 bottles", "Wednesday"),
        ("Quench Bar & Grill, Boardman Ohio", "$2.50 Tito shots", "Tuesday"),
        ("La Villa Tavern, Struthers Ohio", "$2 bottles", "Monday"),

        # NEW — LOS GALLOS
        ("Los Gallos, Boardman Ohio", "$2 bottles", "Monday"),
        ("Los Gallos, Boardman Ohio", "$2 bottles", "Tuesday"),
        ("Los Gallos, Boardman Ohio", "$2 bottles", "Wednesday"),
        ("Los Gallos, Boardman Ohio", "$2 bottles", "Thursday"),
    ]

    specials = []

    for bar_name, deal, day in seed_list:
        lat, lon = geocode_location(bar_name)

        specials.append(
            Special(
                bar_name=bar_name,
                deal=deal,
                day=day,
                latitude=lat,
                longitude=lon,
                verified=True
            )
        )

    db.session.add_all(specials)
    db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


# ----------------------
# ROUTES
# ----------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add_special", methods=["POST"])
def add_special():

    data = request.json

    lat, lon = geocode_location(data["bar_name"])

    special = Special(
        bar_name=data["bar_name"],
        deal=data["deal"],
        day=data["day"].capitalize(),
        latitude=lat,
        longitude=lon,
        verified=False
    )

    db.session.add(special)
    db.session.commit()

    return jsonify({"status": "Saved — Pending Verification"})


@app.route("/get_specials/<day>")
def get_specials(day):

    day = day.capitalize()

    specials = Special.query.filter_by(day=day).all()

    return jsonify([
        {
            "id": s.id,
            "bar_name": s.bar_name,
            "deal": s.deal,
            "verified": s.verified,
            "latitude": s.latitude,
            "longitude": s.longitude
        }
        for s in specials
    ])


if __name__ == "__main__":
    app.run(debug=True)
