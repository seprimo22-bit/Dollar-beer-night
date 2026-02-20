from flask import Flask, request, jsonify, render_template
import sqlite3
import math
import datetime

app = Flask(__name__)

DB = "specials.db"


# ---------- DATABASE SETUP ----------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS specials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            deal TEXT,
            address TEXT,
            day TEXT,
            lat REAL,
            lng REAL
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------- DISTANCE FUNCTION ----------
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi/2)**2 +
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    )

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ---------- ROUTES ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/add_special", methods=["POST"])
def add_special():
    data = request.json

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        INSERT INTO specials (name, deal, address, day, lat, lng)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data["deal"],
        data["address"],
        data["day"].lower(),
        41.1,  # placeholder coords
        -80.6
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "saved"})


@app.route("/api/specials")
def get_specials():

    user_lat = float(request.args.get("lat", 41.1))
    user_lng = float(request.args.get("lng", -80.6))
    today = datetime.datetime.now().strftime("%A").lower()

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT name, deal, address, day, lat, lng FROM specials")
    rows = c.fetchall()

    conn.close()

    results = []

    for r in rows:
        name, deal, address, day, lat, lng = r

        if day != today:
            continue

        dist = haversine(user_lat, user_lng, lat, lng)

        if dist <= 60:
            results.append({
                "name": name,
                "deal": deal,
                "address": address,
                "lat": lat,
                "lng": lng,
                "distance": round(dist, 1)
            })

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
