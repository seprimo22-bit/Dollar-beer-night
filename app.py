from flask import Flask, render_template, request, redirect, jsonify
import json, os, requests
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "bars.json"


# ---------- LOAD / SAVE ----------

def load_bars():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_bars(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- GEOCODING ----------

def geocode(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json"}
        headers = {"User-Agent": "DollarBeerApp"}

        r = requests.get(url, params=params, headers=headers, timeout=5)
        data = r.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])

    except Exception as e:
        print("Geocode error:", e)

    return None, None


# ---------- ROUTES ----------

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
        "day": day.strip(),
        "lat": lat,
        "lng": lng
    })

    save_bars(bars)
    return redirect("/")


@app.route("/bars")
def bars():
    bars = load_bars()
    today = datetime.now().strftime("%A")

    # Case-insensitive day match
    filtered = [
        b for b in bars
        if b.get("day", "").lower() == today.lower()
    ]

    # If none match today, show all (prevents empty map)
    if not filtered:
        filtered = bars

    return jsonify(filtered)


if __name__ == "__main__":
    app.run(debug=True)
