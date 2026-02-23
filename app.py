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
    address = db.Column(db.String(200))
    deal = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ----------------------
# GEOCODING FUNCTION
# ----------------------
def geocode_location(bar, address=None):
    try:
        query = f"{bar}, {address}" if address else bar

        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query,
            "format": "json",
            "limit": 1
        }

        headers = {"User-Agent": "BeerDollarsApp"}

        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass

    return None, None


# ----------------------
# SEED DATA
# ----------------------
def seed_data():
    if Special.query.count() > 0:
        return

    seed = [
        Special(
            bar_name="La Villa Tavern",
            address="Struthers Ohio",
            deal="$2 bottles",
            day="Monday",
            verified=True
        ),
        Special(
            bar_name="Los Gallos",
            address="Boardman Ohio",
            deal="$2 bottles",
            day="Monday",
            verified=True
        )
    ]

    for s in seed:
        lat, lon = geocode_location(s.bar_name, s.address)
        s.latitude = lat
        s.longitude = lon

    db.session.add_all(seed)
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

    lat, lon = geocode_location(
        data["bar_name"],
        data.get("address")
    )

    special = Special(
        bar_name=data["bar_name"],
        address=data.get("address"),
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
            "bar_name": s.bar_name,
            "address": s.address,
            "deal": s.deal,
            "verified": s.verified,
            "latitude": s.latitude,
            "longitude": s.longitude
        }
        for s in specials
    ])


if __name__ == "__main__":
    app.run(debug=True)
