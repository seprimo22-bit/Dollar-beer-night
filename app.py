from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import requests

app = Flask(__name__)
DB = "beer.db"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS specials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            deal TEXT,
            day TEXT,
            address TEXT,
            lat REAL,
            lng REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------------- GEOCODER ----------------
def geocode(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "beer-dollars-app"}

    try:
        r = requests.get(url, params=params, headers=headers)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass

    return None, None

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    deal = request.form["deal"]
    day = request.form["day"]
    address = request.form["address"]

    lat, lng = geocode(address)

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO specials (name, deal, day, address, lat, lng) VALUES (?, ?, ?, ?, ?, ?)",
        (name, deal, day, address, lat, lng)
    )
    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/specials")
def specials():
    day = request.args.get("day")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    if day:
        c.execute("SELECT * FROM specials WHERE day=?", (day,))
    else:
        c.execute("SELECT * FROM specials")

    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "name": r[1],
            "deal": r[2],
            "day": r[3],
            "address": r[4],
            "lat": r[5],
            "lng": r[6]
        })

    return jsonify(results)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
