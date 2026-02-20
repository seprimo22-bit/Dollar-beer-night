from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

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
            price REAL,
            description TEXT,
            category TEXT,
            verified INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# -------------------------
# Home Page
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# Get All Events
# -------------------------
@app.route("/events")
def get_events():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM events ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    events = []
    for r in rows:
        events.append({
            "id": r[0],
            "name": r[1],
            "location": r[2],
            "lat": r[3],
            "lon": r[4],
            "price": r[5],
            "description": r[6],
            "category": r[7],
            "verified": bool(r[8]),
            "created_at": r[9]
        })

    return jsonify(events)


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
        (name, location, latitude, longitude, price, description, category, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("location"),
        data.get("lat"),
        data.get("lon"),
        data.get("price"),
        data.get("description"),
        data.get("category"),  # bar, baseball, hockey, etc.
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return jsonify({"status": "submitted"})


# -------------------------
# Simple Nearby Filter
# (placeholder — real geo later)
# -------------------------
@app.route("/nearby", methods=["POST"])
def nearby():
    lat = float(request.json["lat"])
    lon = float(request.json["lon"])

    # MVP: just return all events for now
    # later add distance calc (Haversine)
    return get_events()


# -------------------------
# Feedback Endpoint
# -------------------------
@app.route("/feedback", methods=["POST"])
def feedback():
    return jsonify({"status": "received"})


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
