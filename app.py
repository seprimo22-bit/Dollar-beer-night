from flask import Flask, request, jsonify, render_template
import json
import os
import math
import requests
from datetime import datetime

app = Flask(__name__)

SPECIALS_FILE = "Specials.json"
GEOCODE_PROVIDER = os.getenv("GEOCODE_PROVIDER", "nominatim")


# ----------------------------
# Load & Save JSON
# ----------------------------

def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []
    with open(SPECIALS_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ----------------------------
# Distance Calculation
# ----------------------------

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ----------------------------
# Geocode Address (Nominatim)
# ----------------------------

def geocode_address(address):
    if GEOCODE_PROVIDER.lower() != "nominatim":
        return None, None

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "DollarBeerNightApp"
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            return float(data[0]["lat"]), float(data[0]["lon"])

    return None, None


# ----------------------------
# Homepage
# ----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# API: Get Specials Near User
# ----------------------------

@app.route("/api/specials")
def get_specials():
    lat = float(request.args.get("lat"))
    lng = float(request.args.get("lng"))

    today = datetime.now().strftime("%A").lower()

    specials = load_specials()
    results = []

    for s in specials:
        if s.get("day", "").lower() != today:
            continue

        distance = haversine(lat, lng, s["lat"], s["lng"])

        if distance <= 100:
            results.append({
                "name": s["name"],
                "deal": s["deal"],
                "address": s["address"],
                "lat": s["lat"],
                "lng": s["lng"],
                "distance": round(distance, 1)
            })

    return jsonify(results)


# ----------------------------
# API: Add Special
# ----------------------------

@app.route("/api/add_special", methods=["POST"])
def add_special():
    data = request.json

    name = data["name"]
    deal = data["deal"]
    address = data["address"]
    day = data["day"].lower()

    lat, lng = geocode_address(address)

    if lat is None or lng is None:
        return jsonify({"error": "Could not geocode address"}), 400

    specials = load_specials()

    specials.append({
        "name": name,
        "deal": deal,
        "address": address,
        "day": day,
        "lat": lat,
        "lng": lng
    })

    save_specials(specials)

    return jsonify({"status": "saved"})


# ----------------------------
# Run
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/debug-specials")
def debug_specials():
    import os, json
    if not os.path.exists("Specials.json"):
        return {"error": "Specials.json not found"}
    with open("Specials.json") as f:
        return json.load(f)
