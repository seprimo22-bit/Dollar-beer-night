from flask import Flask, request, jsonify, render_template
from datetime import datetime
import json
import math
import os

app = Flask(__name__)

SPECIALS_FILE = "Specials.json"


# -------------------------
# Load Specials
# -------------------------
def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []

    with open(SPECIALS_FILE, "r") as f:
        return json.load(f)


# -------------------------
# Save Specials
# -------------------------
def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# -------------------------
# Distance Calculation
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # miles

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# -------------------------
# Home Page
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# Submit New Special
# -------------------------
@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    specials = load_specials()

    new_special = {
        "name": data.get("name"),
        "deal": data.get("deal"),
        "address": data.get("address"),
        "day": data.get("day").lower(),
        "lat": float(data.get("lat")),
        "lng": float(data.get("lng"))
    }

    specials.append(new_special)
    save_specials(specials)

    return jsonify({"status": "saved"})


# -------------------------
# Find Nearby Specials
# -------------------------
@app.route("/nearby", methods=["POST"])
def nearby():
    user_lat = float(request.json["lat"])
    user_lng = float(request.json["lng"])

    today = datetime.now().strftime("%A").lower()

    specials = load_specials()
    results = []

    for bar in specials:
        if bar["day"].lower() != today:
            continue

        distance = haversine(
            user_lat,
            user_lng,
            float(bar["lat"]),
            float(bar["lng"])
        )

        if distance <= 100:  # 100-mile radius
            results.append(bar)

    return jsonify(results)


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
