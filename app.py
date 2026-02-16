from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import json, os, math, datetime

app = Flask(__name__)

DATA_FILE = "specials.json"
geolocator = Nominatim(user_agent="beer_locator")


# ---------- Utility ----------
def load_specials():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/specials", methods=["POST"])
def add_special():
    data = request.json

    # Geocode address automatically
    location = geolocator.geocode(data["address"])
    if not location:
        return jsonify({"error": "Address not found"}), 400

    specials = load_specials()

    specials.append({
        "name": data["name"],
        "deal": data["deal"],
        "address": data["address"],
        "day": data["day"],
        "lat": location.latitude,
        "lng": location.longitude,
        "validated": False,
        "timestamp": datetime.datetime.now().isoformat()
    })

    save_specials(specials)

    return jsonify({"status": "saved"})


@app.route("/api/specials", methods=["GET"])
def get_specials():
    specials = load_specials()

    user_lat = float(request.args.get("lat"))
    user_lng = float(request.args.get("lng"))
    today = datetime.datetime.now().strftime("%A")

    results = []

    for s in specials:
        if s["day"] != today:
            continue

        dist = haversine(user_lat, user_lng, s["lat"], s["lng"])
        if dist <= 60:  # 60 mile radius
            s["distance"] = round(dist, 1)
            results.append(s)

    results.sort(key=lambda x: x["distance"])
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
