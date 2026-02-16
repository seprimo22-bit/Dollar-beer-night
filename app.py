from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import json, os, math, datetime

app = Flask(__name__)

DATA_FILE = "specials.json"
geolocator = Nominatim(user_agent="beer_locator", timeout=5)


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
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/specials", methods=["POST"])
def add_special():
    data = request.json

    try:
        location = geolocator.geocode(data["address"])
    except Exception as e:
        print("Geocode error:", e)
        location = None

    # fallback coords if geocode fails
    lat = location.latitude if location else 41.1
    lng = location.longitude if location else -80.6

    specials = load_specials()

    specials.append({
        "name": data["name"].strip(),
        "deal": data["deal"].strip(),
        "address": data["address"].strip(),
        "day": data["day"].strip().lower(),
        "lat": lat,
        "lng": lng,
        "validated": False,
        "timestamp": datetime.datetime.now().isoformat()
    })

    save_specials(specials)

    print("Saved special:", specials[-1])
    return jsonify({"status": "saved"})


@app.route("/api/specials", methods=["GET"])
def get_specials():
    specials = load_specials()

    user_lat = float(request.args.get("lat", 41.1))
    user_lng = float(request.args.get("lng", -80.6))

    today = datetime.datetime.now().strftime("%A").lower()

    results = []

    for s in specials:
        if s["day"].lower() != today:
            continue

        dist = haversine(user_lat, user_lng, s["lat"], s["lng"])

        if dist <= 60:
            s["distance"] = round(dist, 1)
            results.append(s)

    results.sort(key=lambda x: x["distance"])
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
