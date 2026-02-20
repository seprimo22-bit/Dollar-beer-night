from flask import Flask, request, jsonify, render_template
import json, os, math
from datetime import datetime

app = Flask(__name__)
SPECIALS_FILE = "Specials.json"


def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []
    with open(SPECIALS_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon/2)**2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


@app.route("/")
def home():
    return render_template("index.html")


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

        if "lat" not in s or "lng" not in s:
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


@app.route("/api/add_special", methods=["POST"])
def add_special():
    data = request.json
    specials = load_specials()

    specials.append({
        "name": data["name"],
        "deal": data["deal"],
        "address": data["address"],
        "day": data["day"].lower(),
        "lat": float(data["lat"]),
        "lng": float(data["lng"])
    })

    save_specials(specials)
    return jsonify({"status": "saved"})
