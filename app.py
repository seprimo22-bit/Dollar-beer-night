from flask import Flask, render_template, request, redirect, jsonify
import json, os, requests
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "bars.json"


# ---------- JSON STORAGE ----------

def load_bars():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []


def save_bars(bars):
    with open(DATA_FILE, "w") as f:
        json.dump(bars, f, indent=2)


# ---------- GEOCODING ----------

def geocode(address):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json"}
        headers = {"User-Agent": "BeerFinderApp"}

        r = requests.get(url, params=params, headers=headers, timeout=5)
        data = r.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass

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
def get_bars():
    bars = load_bars()
    today = datetime.now().strftime("%A")

    # Only today's bars
    today_bars = [
        b for b in bars
        if b.get("day", "").lower() == today.lower()
        and b.get("lat") and b.get("lng")
    ]

    return jsonify(today_bars)


if __name__ == "__main__":
    app.run(debug=True)
