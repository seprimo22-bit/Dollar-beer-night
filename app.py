
# app.py
import os
import logging
from flask import Flask, request, jsonify, render_template
from psycopg2 import connect, sql, extras, OperationalError
from twilio.rest import Client

# ---------------------------
# Configuration & Logging
# ---------------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Database
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://beer_dollars_db_user:vbldLdTI705VOj3B1e4IphF7X9GK3pZw@dpg-d6e37ipr0fns73d6scc0-a/beer_dollars_db"
)

# Twilio (for slash screen verification)
TWILIO_SID = os.environ.get("TWILIO_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN) if TWILIO_SID and TWILIO_AUTH_TOKEN else None
MASTER_OVERRIDE_CODE = "999"

# ---------------------------
# Database Helper Functions
# ---------------------------
def get_db_connection():
    try:
        conn = connect(DATABASE_URL, cursor_factory=extras.RealDictCursor)
        return conn
    except OperationalError as e:
        app.logger.error(f"Database connection failed: {e}")
        return None

def create_tables():
    conn = get_db_connection()
    if not conn:
        return
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bars (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude DOUBLE PRECISION,
            longitude DOUBLE PRECISION
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id SERIAL PRIMARY KEY,
            bar_id INT REFERENCES bars(id) ON DELETE CASCADE,
            day_of_week TEXT NOT NULL,
            description TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            phone_number TEXT UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Initialize tables on startup
create_tables()

# ---------------------------
# Routes
# ---------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/slash", methods=["GET", "POST"])
def slash():
    if request.method == "POST":
        phone = request.form.get("phone")
        code = request.form.get("code")

        if code == MASTER_OVERRIDE_CODE:
            return jsonify({"success": True, "message": "Master override entered!"})

        if not phone:
            return jsonify({"success": False, "message": "Phone number required"}), 400

        # Send Twilio code
        if twilio_client:
            verification_code = "123456"  # For demo, you can generate a real random code
            try:
                twilio_client.messages.create(
                    body=f"Your Beer Dollars verification code is {verification_code}",
                    from_=TWILIO_PHONE_NUMBER,
                    to=phone
                )
                return jsonify({"success": True, "message": "Code sent!"})
            except Exception as e:
                app.logger.error(f"Twilio error: {e}")
                return jsonify({"success": False, "message": "Failed to send code"}), 500
        else:
            return jsonify({"success": False, "message": "Twilio not configured"}), 500

    return render_template("slash.html")

# Get bars & deals
@app.route("/api/bars", methods=["GET"])
def get_bars():
    day = request.args.get("day")
    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "DB connection failed"}), 500
    cur = conn.cursor()
    try:
        if day:
            query = """
                SELECT b.id, b.name, b.address, b.latitude, b.longitude,
                       d.day_of_week, d.description
                FROM bars b
                LEFT JOIN deals d ON b.id = d.bar_id
                WHERE d.day_of_week = %s
            """
            cur.execute(query, (day,))
        else:
            query = """
                SELECT b.id, b.name, b.address, b.latitude, b.longitude,
                       d.day_of_week, d.description
                FROM bars b
                LEFT JOIN deals d ON b.id = d.bar_id
            """
            cur.execute(query)
        results = cur.fetchall()
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Error fetching bars: {e}")
        return jsonify({"success": False, "message": "Query failed"}), 500
    finally:
        cur.close()
        conn.close()

# Add bar
@app.route("/api/bars", methods=["POST"])
def add_bar():
    data = request.get_json()
    name = data.get("name")
    address = data.get("address")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    deals = data.get("deals", {})  # e.g., {"Monday": "$2 Beer"}

    if not name or not address:
        return jsonify({"success": False, "message": "Name and address required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "DB connection failed"}), 500
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO bars (name, address, latitude, longitude) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, address, latitude, longitude)
        )
        bar_id = cur.fetchone()["id"]

        # Insert deals
        for day, desc in deals.items():
            if desc.strip() == "":
                continue
            cur.execute(
                "INSERT INTO deals (bar_id, day_of_week, description) VALUES (%s, %s, %s)",
                (bar_id, day, desc)
            )
        conn.commit()
        return jsonify({"success": True, "message": "Bar added!", "bar_id": bar_id})
    except Exception as e:
        app.logger.error(f"Error adding bar: {e}")
        return jsonify({"success": False, "message": "Failed to add bar"}), 500
    finally:
        cur.close()
        conn.close()

# ---------------------------
# Health Check
# ---------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# ---------------------------
# Run
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
