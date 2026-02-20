from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import math

app = Flask(__name__)
DATABASE = "beer.db"


# -------------------------
# Database Setup
# -------------------------
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS specials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bar_name TEXT,
            special TEXT,
            address TEXT,
            days TEXT,
            latitude REAL,
            longitude REAL,
            created_at TEXT,
            verified INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# Homepage
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# Submit Special
# -------------------------
@app.route("/submit", methods=["POST"])
def submit_special():
    data = request.json

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
        INSERT INTO specials
        (bar_name, special, address, days, latitude, longitude, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("bar_name"),
        data.get("special"),
        data.get("address"),
        data.get("days"),
        data.get("lat"),
        data.get("lon"),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})


# -------------------------
# Get All Specials
# -------------------------
@app.route("/specials")
def get_specials():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM specials ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "bar_name": r[1],
            "special": r[2],
            "address": r[3],
            "days": r[4],
            "lat": r[5],
            "lon": r[6],
            "created_at": r[7],
            "verified": bool(r[8])
        })

    return jsonify(results)


# -------------------------
# Nearby Search (Map Button)
# -------------------------
def distance(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon/2)**2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


@app.route("/nearby", methods=["POST"])
def nearby():
    lat = float(request.json["lat"])
    lon = float(request.json["lon"])

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM specials")
    rows = c.fetchall()
    conn.close()

    nearby_results = []

    for r in rows:
        if r[5] and r[6]:
            d = distance(lat, lon, r[5], r[6])
            if d < 50:  # 50 km radius (adjust anytime)
                nearby_results.append({
                    "bar_name": r[1],
                    "special": r[2],
                    "address": r[3],
                    "days": r[4],
                    "distance_km": round(d, 2)
                })

    return jsonify(nearby_results)


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
