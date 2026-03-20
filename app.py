from flask import Flask, render_template, request, jsonify
from config import Config
from models import db, Bar
import os
import requests

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# --- Ensure tables are created only once ---
tables_created = False
@app.before_request
def create_tables_once():
    global tables_created
    if not tables_created:
        db.create_all()
        tables_created = True


# --- Google Geocoding Helper ---
def geocode_address(address):
    api_key = app.config["GOOGLE_MAPS_API_KEY"]
    if not api_key or not address:
        return None, None

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    resp = requests.get(url, params=params).json()

    if resp.get("status") == "OK" and resp["results"]:
        loc = resp["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]

    return None, None


# --- Routes ---

# Main user interface
@app.route("/")
def index():
    return render_template("index.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])


# Admin interface
@app.route("/admin")
def admin():
    return render_template("admin.html")


# Get bars for a given day
@app.route("/api/bars/<day>")
def get_bars(day):
    bars = Bar.query.filter_by(day=day).all()
    result = [{
        "id": bar.id,
        "name": bar.name,
        "address": bar.address,
        "deal": bar.deal,
        "day": bar.day,
        "lat": bar.lat,
        "lng": bar.lng,
        "paid": bar.paid
    } for bar in bars]

    return jsonify(result)


# Add a new bar
@app.route("/api/add_bar", methods=["POST"])
def add_bar():
    data = request.get_json()

    lat = data.get("lat")
    lng = data.get("lng")

    # If no coordinates provided, geocode the address
    if (lat is None or lng is None) and data.get("address"):
        lat, lng = geocode_address(data["address"])

    bar = Bar(
        name=data.get("name"),
        address=data.get("address"),
        deal=data.get("deal"),
        day=data.get("day"),
        lat=lat,
        lng=lng,
        paid=data.get("paid", False)
    )

    db.session.add(bar)
    db.session.commit()

    return jsonify({"status": "success", "id": bar.id})


# Delete a bar
@app.route("/api/delete_bar/<int:bar_id>", methods=["DELETE"])
def delete_bar(bar_id):
    bar = Bar.query.get(bar_id)
    if bar:
        db.session.delete(bar)
        db.session.commit()
        return jsonify({"status": "deleted"})
    return jsonify({"status": "not found"}), 404


# Update a bar
@app.route("/api/update_bar/<int:bar_id>", methods=["PUT"])
def update_bar(bar_id):
    bar = Bar.query.get(bar_id)
    if not bar:
        return jsonify({"status": "not found"}), 404

    data = request.get_json()

    bar.name = data.get("name", bar.name)
    bar.address = data.get("address", bar.address)
    bar.deal = data.get("deal", bar.deal)
    bar.day = data.get("day", bar.day)

    # Update coordinates if provided
    if "lat" in data and "lng" in data:
        bar.lat = data.get("lat")
        bar.lng = data.get("lng")

    bar.paid = data.get("paid", bar.paid)

    db.session.commit()

    return jsonify({"status": "updated", "id": bar.id})


# --- Run app ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
