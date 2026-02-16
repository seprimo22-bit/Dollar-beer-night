from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime
from geopy.geocoders import Nominatim
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

DB = "bars.db"
geolocator = Nominatim(user_agent="beer_locator")


# ---------------- DATABASE SETUP ----------------
def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS specials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            deal TEXT,
            address TEXT,
            day TEXT,
            lat REAL,
            lng REAL,
            validated INTEGER DEFAULT 0,
            timestamp TEXT
        )
        """)

init_db()


# ---------------- DISTANCE FUNCTION ----------------
def miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/add", methods=["POST"])
def add_special():
    data = request.json

    try:
        location = geolocator.geocode(data["address"])
        if not location:
            return jsonify({"error": "Address not found"}), 400

        lat, lng = location.latitude, location.longitude

        with sqlite3.connect(DB) as conn:
            conn.execute("""
                INSERT INTO specials
                (name, deal, address, day, lat, lng, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["name"],
                data["deal"],
                data["address"],
                data["day"],
                lat,
                lng,
                datetime.datetime.now().isoformat()
            ))

        return jsonify({"status": "saved"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/find")
def find_beers():
    user_lat = float(request.args.get("lat"))
    user_lng = float(request.args.get("lng"))
    today = datetime.datetime.now().strftime("%A")

    with sqlite3.connect(DB) as conn:
        rows = conn.execute(
            "SELECT name, deal, address, day, lat, lng, validated FROM specials WHERE day=?",
            (today,)
        ).fetchall()

    results = []
    for r in rows:
        dist = miles(user_lat, user_lng, r[4], r[5])
        if dist <= 60:
            results.append({
                "name": r[0],
                "deal": r[1],
                "address": r[2],
                "lat": r[4],
                "lng": r[5],
                "validated": bool(r[6]),
                "distance": round(dist, 1)
            })

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
