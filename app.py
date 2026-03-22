import os
import json
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from twilio.rest import Client
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")

# -----------------------------
# ENVIRONMENT VARIABLES
# -----------------------------
GOOGLE_MAPS_KEY = os.environ.get("GOOGLE_MAPS_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_AUTH = os.environ.get("TWILIO_AUTH")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")

SPECIALS_FILE = "specials.json"


# -----------------------------
# UTILITY: LOAD / SAVE SPECIALS
# -----------------------------
def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []
    with open(SPECIALS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []


def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -----------------------------
# UTILITY: GEOCODE ADDRESS
# -----------------------------
def geocode_address(address):
    if not address:
        return None, None

    url = (
        f"https://maps.googleapis.com/maps/api/geocode/json"
        f"?address={address}&key={GOOGLE_MAPS_KEY}"
    )

    r = requests.get(url).json()

    if r["status"] != "OK":
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

    # Generate a simple 4-digit code
    code = "0000"  # For now, always 0000 (you can randomize later)
    session["verify_code"] = code

    # Send via Twilio
    try:
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
# VERIFY CODE
# -----------------------------
@app.route("/verify_code", methods=["POST"])
def verify_code():
    code = request.json.get("code")
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
    data = load_specials()
    return jsonify(data)


# -----------------------------
# API: ADD SPECIAL
# -----------------------------
@app.route("/add_special", methods=["POST"])
def add_special():
    data = request.json

    name = data.get("name")
    address = data.get("address")
    deal = data.get("deal")
    day = data.get("day")
    lat = data.get("lat")
    lng = data.get("lng")

    if not name or not deal or not day:
        return jsonify({"error": "Missing required fields"}), 400

    # If no lat/lng, geocode from address
    if (not lat or not lng) and address:
        lat, lng = geocode_address(address)

    if not lat or not lng:
        return jsonify({"error": "Could not determine location"}), 400

    specials = load_specials()

    new_entry = {
        "name": name,
        "address": address or "",
        "deal": deal,
        "day": day,
        "lat": lat,
        "lng": lng
    }

    specials.append(new_entry)
    save_specials(specials)

    return jsonify({"success": True})


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
