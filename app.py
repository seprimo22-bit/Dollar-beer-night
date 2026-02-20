from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import math
import os

app = Flask(__name__)

DATABASE = "events.db"


# -------------------------
# Database Init
# -------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            price TEXT,
            description TEXT,
            day TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# Distance Calculation
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
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
def submit_event():
    data = request.json

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
        INSERT INTO events
        (name, location, latitude, longitude, price, description, day, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("location"),
        data.get("lat"),
        data.get("lon"),
        data.get("price"),
        data.get("description"),
        data.get("day").lower(),  # store lowercase for consistency
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "submitted"})


# -------------------------
# Nearby Filter (Day + Radius)
# -------------------------
@app.route("/nearby", methods=["POST"])
def nearby():
    user_lat = float(request.json["lat"])
    user_lon = float(request.json["lon"])

    today = datetime.now().strftime("%A").lower()

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM events")
    rows = c.fetchall()
    conn.close()

    results = []

    for r in rows:
        event_day = (r[7] or "").lower()

        if event_day != today:
            continue

        event_lat = r[3]
        event_lon = r[4]

        if event_lat is None or event_lon is None:
            continue

        distance = haversine(user_lat, user_lon, event_lat, event_lon)

        if distance <= 100:  # 100-mile radius
            results.append({
                "id": r[0],
                "name": r[1],
                "location": r[2],
                "lat": event_lat,
                "lon": event_lon,
                "price": r[5],
                "description": r[6],
                "day": r[7]
            })

    return jsonify(results)


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
