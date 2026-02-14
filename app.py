from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
import math

app = Flask(__name__, template_folder="templates")

DB = "specials.db"


# -----------------------------
# Database setup
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS specials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bar TEXT,
            price TEXT,
            day TEXT,
            notes TEXT,
            lat REAL,
            lon REAL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -----------------------------
# Home page
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Add bar special
# -----------------------------
@app.route("/add", methods=["POST"])
def add_special():
    bar = request.form.get("bar")
    price = request.form.get("price")
    day = request.form.get("day")
    notes = request.form.get("notes")
    lat = request.form.get("lat")
    lon = request.form.get("lon")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT INTO specials (bar, price, day, notes, lat, lon)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (bar, price, day, notes, lat, lon))

    conn.commit()
    conn.close()

    return redirect("/")


# -----------------------------
# Distance calculation
# -----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 3959  # miles
    lat1, lon1, lat2, lon2 = map(
        math.radians,
        [float(lat1), float(lon1), float(lat2), float(lon2)]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1) *
        math.cos(lat2) *
        math.sin(dlon / 2) ** 2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# -----------------------------
# Get nearby specials
# -----------------------------
@app.route("/specials")
def get_specials():
    user_lat = request.args.get("lat")
    user_lon = request.args.get("lon")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT bar, price, day, notes, lat, lon
        FROM specials
        WHERE lat IS NOT NULL
    """)

    rows = c.fetchall()
    conn.close()

    if not user_lat:
        return jsonify(rows)

    results = []
    for r in rows:
        distance = haversine(user_lat, user_lon, r[4], r[5])
        results.append(list(r) + [round(distance, 2)])

    results.sort(key=lambda x: x[6])

    return jsonify(results)


# -----------------------------
# Health check for Render
# -----------------------------
@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
