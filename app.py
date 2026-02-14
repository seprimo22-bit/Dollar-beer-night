from flask import Flask, render_template, request, redirect, jsonify
import os
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# Database choice:
# PostgreSQL if DATABASE_URL exists (Render DB)
# Otherwise fallback SQLite (local dev)

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import psycopg2
else:
    import sqlite3

app = Flask(__name__, template_folder="templates")


# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect("specials.db")


# -----------------------------
# DISTANCE CALCULATION
# -----------------------------
def distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # miles

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) \
        * cos(radians(lat2)) * sin(dlon/2)**2

    return R * 2 * atan2(sqrt(a), sqrt(1-a))


# -----------------------------
# DATABASE INIT
# -----------------------------
def init_db():
    conn = get_db()
    c = conn.cursor()

    if DATABASE_URL:
        c.execute("""
            CREATE TABLE IF NOT EXISTS specials (
                id SERIAL PRIMARY KEY,
                bar TEXT,
                price TEXT,
                day TEXT,
                notes TEXT,
                lat FLOAT,
                lon FLOAT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS specials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bar TEXT,
                price TEXT,
                day TEXT,
                notes TEXT,
                lat FLOAT,
                lon FLOAT,
                created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    conn.close()


init_db()


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# ADD BAR SPECIAL
# -----------------------------
@app.route("/add", methods=["POST"])
def add_special():
    bar = request.form.get("bar")
    price = request.form.get("price")
    day = request.form.get("day")
    notes = request.form.get("notes")
    lat = request.form.get("lat")
    lon = request.form.get("lon")

    conn = get_db()
    c = conn.cursor()

    if DATABASE_URL:
        c.execute("""
            INSERT INTO specials
            (bar, price, day, notes, lat, lon)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (bar, price, day, notes, lat, lon))
    else:
        c.execute("""
            INSERT INTO specials
            (bar, price, day, notes, lat, lon)
            VALUES (?,?,?,?,?,?)
        """, (bar, price, day, notes, lat, lon))

    conn.commit()
    conn.close()

    return redirect("/")


# -----------------------------
# GET SPECIALS NEAR USER
# -----------------------------
@app.route("/specials")
def get_specials():
    user_lat = request.args.get("lat", type=float)
    user_lon = request.args.get("lon", type=float)

    conn = get_db()
    c = conn.cursor()

    c.execute("""
        SELECT bar, price, day, notes, lat, lon
        FROM specials
    """)

    bars = c.fetchall()
    conn.close()

    results = []

    for b in bars:
        if user_lat and user_lon and b[4] and b[5]:
            dist = distance(user_lat, user_lon, float(b[4]), float(b[5]))
            results.append((*b, round(dist, 2)))
        else:
            results.append((*b, None))

    # Sort closest first
    results.sort(key=lambda x: x[6] if x[6] else 999)

    return jsonify(results)


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.route("/health")
def health():
    return "OK", 200


# -----------------------------
# LOCAL RUN ONLY
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
