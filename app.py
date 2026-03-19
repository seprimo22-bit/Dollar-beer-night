from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__, static_folder="static", static_url_path="/static")

# --------------------
# CONFIGURATION
# --------------------
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///beer.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


# --------------------
# DATABASE MODELS
# --------------------
class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    deal = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    highlighted = db.Column(db.Boolean, default=False)  # Paid promotion
    verified = db.Column(db.Boolean, default=False)


# --------------------
# DATABASE INITIALIZATION
# --------------------
with app.app_context():
    db.create_all()


# --------------------
# GOOGLE MAPS GEOCODER
# --------------------
def geocode_address(address):
    if not GOOGLE_MAPS_API_KEY:
        print("Error: GOOGLE_MAPS_API_KEY not set")
        return None, None
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": GOOGLE_MAPS_API_KEY}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("status") == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    except Exception as e:
        print("Geocode error:", e)
    return None, None


# --------------------
# ROUTES
# --------------------

# Splash / loading screen (can be replaced with animation)
@app.route("/splash")
def splash():
    return render_template("splash.html")


# Main user interface
@app.route("/")
def home():
    return render_template("index.html")


# Add new bar/deal (from user input or pin)
@app.route("/add_bar", methods=["POST"])
def add_bar():
    data = request.json
    name = data.get("name", "").strip()
    address = data.get("address", "").strip()
    deal = data.get("deal", "").strip()
    day = data.get("day", "").capitalize().strip()
    lat = data.get("lat")
    lng = data.get("lng")
    highlighted = data.get("highlighted", False)

    if not name or not deal or not day:
        return jsonify(success=False, error="Missing required fields")

    # Geocode if lat/lng not provided
    if lat is None or lng is None:
        queries = [f"{name} {address}", f"{name} near {address}", address, name]
        for q in queries:
            lat, lng = geocode_address(q)
            if lat is not None:
                break

    new_bar = Bar(
        name=name,
        address=address,
        deal=deal,
        day=day,
        latitude=lat,
        longitude=lng,
        highlighted=highlighted,
    )
    db.session.add(new_bar)
    db.session.commit()
    return jsonify(success=True, bar_id=new_bar.id)


# Get all bars for a specific day
@app.route("/get_bars/<day>")
def get_bars(day):
    bars = Bar.query.filter_by(day=day.capitalize()).all()
    return jsonify([
        {
            "id": b.id,
            "name": b.name,
            "address": b.address,
            "lat": b.latitude,
            "lng": b.longitude,
            "deal": b.deal,
            "highlighted": b.highlighted,
            "verified": b.verified
        }
        for b in bars
    ])


# Admin interface
@app.route("/admin")
def admin():
    bars = Bar.query.all()
    return render_template("admin.html", bars=bars)


# Edit bar/deal in admin
@app.route("/edit_bar/<int:bar_id>", methods=["POST"])
def edit_bar(bar_id):
    bar = Bar.query.get_or_404(bar_id)
    bar.name = request.form.get("name", bar.name).strip()
    bar.address = request.form.get("address", bar.address).strip()
    bar.deal = request.form.get("deal", bar.deal).strip()
    bar.day = request.form.get("day", bar.day).capitalize().strip()
    bar.highlighted = "highlighted" in request.form
    bar.verified = "verified" in request.form

    if bar.address:
        lat, lng = geocode_address(f"{bar.name} {bar.address}")
        bar.latitude = lat
        bar.longitude = lng

    db.session.commit()
    return redirect(url_for("admin"))


# Delete bar/deal
@app.route("/delete_bar/<int:bar_id>", methods=["POST"])
def delete_bar(bar_id):
    bar = Bar.query.get_or_404(bar_id)
    db.session.delete(bar)
    db.session.commit()
    return redirect(url_for("admin"))


# --------------------
# RUN APP
# --------------------
if __name__ == "__main__":
    app.run(debug=True)
