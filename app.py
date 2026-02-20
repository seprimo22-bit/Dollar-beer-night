from flask import Flask, request, jsonify, render_template
from datetime import datetime
import json, math, os

app = Flask(__name__)

SPECIALS_FILE = "Specials.json"


# ---------- Load Specials ----------
def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []
    with open(SPECIALS_FILE, "r") as f:
        return json.load(f)


# ---------- Save Specials ----------
def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- Distance Formula ----------
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


# ---------- Home ----------
@app.route("/")
def home():
    return render_template("index.html")


# ---------- FIND SPECIALS (matches index.html fetch) ----------
@app.route("/api/specials")
def get_specials():
    user_lat = float(request.args.get("lat"))
    user_lng = float(request.args.get("lng"))

    today = datetime.now().strftime("%A").lower()
    specials = load_specials()

    results = []

    for bar in specials:
        if bar.get("day","").lower() != today:
            continue

        dist = haversine(
            user_lat,
            user_lng,
            float(bar["lat"]),
            float(bar["lng"])
        )

        if dist <= 100:
            bar_copy = dict(bar)
            bar_copy["distance"] = round(dist, 1)
            results.append(bar_copy)

    return jsonify(results)


# ---------- ADD SPECIAL (matches index.html fetch) ----------
@app.route("/api/add_special", methods=["POST"])
def add_special():
    data = request.json
    specials = load_specials()

    new_special = {
        "name": data.get("name"),
        "deal": data.get("deal"),
        "address": data.get("address"),
        "day": data.get("day").lower(),

        # fallback coords if frontend didn't send them
        "lat": float(data.get("lat", 41.02)),
        "lng": float(data.get("lng", -80.66))
    }

    specials.append(new_special)
    save_specials(specials)

    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(debug=True)
