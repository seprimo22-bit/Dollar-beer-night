from flask import Flask, request, jsonify, render_template
import json, os, math
from datetime import datetime

app = Flask(__name__)
SPECIALS_FILE = "Specials.json"


# ---------- Load JSON ----------
def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []
    with open(SPECIALS_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- Distance ----------
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
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


# ---------- Homepage ----------
@app.route("/")
def home():
    return render_template("index.html")


# ---------- Get specials near user ----------
@app.route("/api/specials")
def specials():
    lat = float(request.args.get("lat"))
    lng = float(request.args.get("lng"))
    today = datetime.now().strftime("%A").lower()

    specials = load_specials()
    results = []

    for s in specials:
        if s.get("day", "").lower() != today:
            continue

        dist = haversine(lat, lng, s["lat"], s["lng"])

        if dist <= 100:
            s["distance"] = round(dist, 1)
            results.append(s)

    return jsonify(results)


# ---------- Add special ----------
@app.route("/api/add_special", methods=["POST"])
def add_special():
    data = request.json
    specials = load_specials()

    new_special = {
        "name": data["name"],
        "deal": data["deal"],
        "address": data["address"],
        "day": data["day"].lower(),
        "lat": data.get("lat", 41.02),
        "lng": data.get("lng", -80.66)
    }

    specials.append(new_special)
    save_specials(specials)

    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(debug=True)
