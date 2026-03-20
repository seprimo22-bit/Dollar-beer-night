from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import googlemaps
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# ---------------- DATABASE ----------------
class Special(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    deal = db.Column(db.String(100))
    day = db.Column(db.String(10))
    address = db.Column(db.String(200))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    promotion = db.Column(db.String(10), default='none')

db.create_all()

# ---------------- GEOCODE ----------------
def geocode(address):
    try:
        result = gmaps.geocode(address)
        if result:
            loc = result[0]['geometry']['location']
            return loc['lat'], loc['lng']
    except Exception as e:
        print("Geocode error:", e)
    return None, None

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/add", methods=["POST"])
def add():
    data = request.get_json() or request.form
    name = data.get("name")
    deal = data.get("deal")
    day = data.get("day")
    address = data.get("address", "")
    promotion = data.get("promotion", "none")
    lat = data.get("lat")
    lng = data.get("lng")

    # Combine address fields if provided
    if not lat or not lng:
        street = data.get("street", "")
        city = data.get("city", "")
        state = data.get("state", "")
        zip_code = data.get("zip", "")
        full_address = f"{street}, {city}, {state} {zip_code}"
        lat, lng = geocode(full_address)
        if not address:
            address = full_address

    special = Special(
        name=name,
        deal=deal,
        day=day,
        address=address,
        lat=lat,
        lng=lng,
        promotion=promotion
    )
    db.session.add(special)
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/specials")
def specials():
    day = request.args.get("day")
    query = Special.query
    if day:
        query = query.filter_by(day=day)
    specials_list = query.all()
    results = []
    for s in specials_list:
        results.append({
            "id": s.id,
            "name": s.name,
            "deal": s.deal,
            "day": s.day,
            "address": s.address,
            "lat": s.lat,
            "lng": s.lng,
            "promotion": s.promotion
        })
    return jsonify(results)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
