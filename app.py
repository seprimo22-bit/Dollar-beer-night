
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import os
import psycopg2
import psycopg2.extras
import json
from twilio.rest import Client
from datetime import datetime, time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

DATABASE_URL = os.environ.get("DATABASE_URL")

TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")

client = Client(TWILIO_SID, TWILIO_TOKEN)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# ------------------ AUTH ROUTES ------------------
@app.route("/")
def slash():
    if session.get("verified"):
        return redirect("/home")
    return render_template("slash.html")

@app.route("/verify-code", methods=["POST"])
def verify_code():
    number = request.form.get("phone")
    code = request.form.get("code")
    if code == "999":  # master override
        session["verified"] = True
        return redirect("/home")

    # Here you could verify with Twilio stored code (mocked for simplicity)
    # Assume code sent via SMS and stored in session temporarily
    if session.get("twilio_code") == code:
        session["verified"] = True
        return redirect("/home")
    return render_template("slash.html", error="Incorrect code")

@app.route("/send-code", methods=["POST"])
def send_code():
    number = request.form.get("phone")
    code = "123456"  # for simplicity, generate random in prod
    session["twilio_code"] = code
    # Uncomment for real Twilio:
    # client.messages.create(to=number, from_=TWILIO_NUMBER, body=f"Your Beer Dollars code: {code}")
    return jsonify({"success": True, "message": f"Code sent to {number} (demo: {code})"})

# ------------------ APP ROUTES ------------------
@app.route("/home")
def home():
    if not session.get("verified"):
        return redirect("/")
    return render_template("index.html")

@app.route("/get-bars")
def get_bars():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT bar_name AS bar, lat, lng, deals FROM bars")
        bars = cur.fetchall()
        for bar in bars:
            if isinstance(bar['deals'], str):
                bar['deals'] = json.loads(bar['deals'])
        cur.close()
        conn.close()
        return jsonify(bars)
    except Exception as e:
        print("Error fetching bars:", e)
        return jsonify([]), 500

@app.route("/add-bar", methods=["POST"])
def add_bar():
    data = request.get_json()
    required_fields = ["bar", "lat", "lng", "deals"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bars (bar_name, lat, lng, deals) VALUES (%s,%s,%s,%s)",
            (data['bar'], data['lat'], data['lng'], json.dumps(data['deals']))
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        print("Error adding bar:", e)
        return jsonify({"error": "Database error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
