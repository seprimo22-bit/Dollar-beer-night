from flask import Flask, render_template, request, redirect, jsonify
import json, os, requests
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "bars.json"

# Load saved bars
def load_bars():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

# Save bars
def save_bars(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Simple geocoder (OpenStreetMap free API)
def geocode(address):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    try:
        r = requests.get(url, headers={"User-Agent": "beer-app"}).json()
        if r:
            return float(r[0]["lat"]), float(r[0]["lon"])
    except:
        pass
    return None, None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add", methods=["POST"])
def add_bar():
    bars = load_bars()

    name = request.form["name"]
    special = request.form["special"]
    address = request.form["address"]
    day = request.form["day"]

    lat, lng = geocode(address)

    bars.append({
        "name": name,
        "special": special,
        "address": address,
        "day": day,
        "lat": lat,
        "lng": lng
    })

    save_bars(bars)
    return redirect("/")


@app.route("/bars")
def bars():
    bars = load_bars()
    today = datetime.now().strftime("%A")

    # Only show today's specials
    filtered = [b for b in bars if b["day"] == today]

    return jsonify(filtered)


if __name__ == "__main__":
    app.run(debug=True)
