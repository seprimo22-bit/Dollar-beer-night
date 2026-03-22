import os
import json
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

# -----------------------------
# ENVIRONMENT VARIABLES
# -----------------------------
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_AUTH = os.environ.get("TWILIO_AUTH")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
MASTER_CODE = os.environ.get("MASTER_CODE", "9999")
DATABASE_URL = os.environ.get("DATABASE_URL")

# -----------------------------
# DB CONNECTION
# -----------------------------
def get_db_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL not set")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS specials (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            deal TEXT NOT NULL,
            day TEXT NOT NULL,
            lat DOUBLE PRECISION NOT NULL,
            lng DOUBLE PRECISION NOT NULL
        );
        """
    )
    conn.commit()
    cur.close()
    conn.close()

init_db()

# -----------------------------
# UTILITY: GEOCODE ADDRESS
# -----------------------------
def geocode_address(address):
    if not address or not GOOGLE_MAPS_KEY:
        return None, None

    url = (
        "https://maps.googleapis.com/maps/api/geocode/json"
        f"?address={address}&key={GOOGLE_MAPS_KEY}"
    )

    r = requests.get(url).json()
    if r.get("status") != "OK":
        return None, None

    location = r["results"][0]["geometry"]["location"]
    return location["lat"], location["lng"]

# -----------------------------
# SPLASH SCREEN
# -----------------------------
@app.route("/")
def splash():
    return render_template("splash.html")

# -----------------------------
# PHONE VERIFICATION (SEND CODE)
# -----------------------------
@app.route("/send_code", methods=["POST"])
def send_code():
    phone = request.json.get("phone")
    if not phone:
        return jsonify({"error": "Missing phone"}), 400

    code = "0000"
    session["verify_code"] = code

    try:
        if TWILIO_SID and TWILIO_AUTH and TWILIO_NUMBER:
            client = Client(TWILIO_SID, TWILIO_AUTH)
            client.messages.create(
                body=f"Your Beer Dollars verification code is: {code}",
                from_=TWILIO_NUMBER,
                to=phone
            )
    except Exception as e:
        print("Twilio error:", e)
        return jsonify({"error": "Failed to send code"}), 500

    return jsonify({"success": True})

# -----------------------------
# VERIFY CODE (WITH MASTER OVERRIDE)
# -----------------------------
@app.route("/verify_code", methods=["POST"])
def verify_code():
    code = request.json.get("code")

    if code == MASTER_CODE:
        session["verified"] = True
        return jsonify({"success": True, "override": True})

    if code == session.get("verify_code"):
        session["verified"] = True
        return jsonify({"success": True})

    return jsonify({"success": False}), 401

# -----------------------------
# MAIN MAP PAGE
# -----------------------------
@app.route("/index")
def index():
    if not session.get("verified"):
        return redirect(url_for("splash"))
    return render_template("index.html", GOOGLE_MAPS_KEY=GOOGLE_MAPS_KEY)

# -----------------------------
# ADMIN PAGE
# -----------------------------
@app.route("/admin")
def admin():
    return render_template("admin.html")

# -----------------------------
# API: GET SPECIALS
# -----------------------------
@app.route("/get_specials")
def get_specials():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, address, deal, day, lat, lng FROM specials ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)

# -----------------------------
# API: ADD SPECIAL
# -----------------------------
@app.route("/add_special", methods=["POST"])
def add_special():
    data = request.json or {}

    name = data.get("name")
    address = data.get("address")
    deal = data.get("deal")
    day = data.get("day")
    lat = data.get("lat")
    lng = data.get("lng")

    if not name or not deal or not day:
        return jsonify({"error": "Missing required fields"}), 400

    if (not lat or not lng) and address:
        lat, lng = geocode_address(address)

    if not lat or not lng:
        return jsonify({"error": "Could not determine location"}), 400

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO specials (name, address, deal, day, lat, lng)
        VALUES (%s, %s, %s, %s, %s, %s);
        """,
        (name, address or "", deal, day, float(lat), float(lng))
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True})

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

