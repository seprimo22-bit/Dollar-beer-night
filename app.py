import sqlite3
from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2

app = Flask(__name__)

DB = "beer.db"


# ----------------------------
# DATABASE SETUP
# ----------------------------
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


# ----------------------------
# DISTANCE CALCULATOR
# ----------------------------
def distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(float(lat2) - float(lat1))
    dlon = radians(float(lon2) - float(lon1))

    a = sin(dlat/2)**2 + cos(radians(float(lat1))) \
        * cos(radians(float(lat2))) * sin(dlon/2)**2

    return R * 2 * atan2(sqrt(a), sqrt(1-a))


# ----------------------------
# HOME PAGE
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ----------------------------
# ADD SPECIAL
# ----------------------------
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

    c.execute(
        "INSERT INTO specials (bar, price, day, notes, lat, lon) VALUES (?, ?, ?, ?, ?, ?)",
        (bar, price, day, notes, lat, lon),
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ----------------------------
# VIEW SPECIALS
# ----------------------------
@app.route("/specials")
def view_specials():

    today = datetime.now().strftime("%A")
    user_lat = request.args.get("lat")
    user_lon = request.args.get("lon")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        SELECT bar, price, day, notes, lat, lon
        FROM specials
        WHERE day LIKE ?
        ORDER BY id DESC
    """, (f"%{today}%",))

    data = c.fetchall()
    conn.close()

    filtered = []

    for row in data:
        if user_lat and user_lon and row[4] and row[5]:
            if distance(user_lat, user_lon, row[4], row[5]) < 60:
                filtered.append(row)
        else:
            filtered.append(row)

    return jsonify(filtered)


# ----------------------------
# RENDER DEPLOYMENT ENTRY
# ----------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
