from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import os

app = Flask(__name__)

# ----------------------
# DATABASE CONFIG
# Use Render PostgreSQL if available
# ----------------------
database_url = os.getenv("DATABASE_URL")

if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace("postgres://", "postgresql://")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beer.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------------
# MODEL
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
# GEOCODE
# ----------------------
def geocode_location(query):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 1}
        headers = {"User-Agent": "BeerDollarsApp"}

        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass

    return None, None


# ----------------------
# INIT DB
# ----------------------
with app.app_context():
    db.create_all()


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
