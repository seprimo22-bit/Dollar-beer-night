import os
from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from dotenv import load_dotenv
import psycopg
from twilio.rest import Client

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "brick_truth_99")

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Twilio config
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID else None

# ===============================
# DATABASE CONNECTION
# ===============================
def get_db_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL not set")
    conn_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return psycopg.connect(conn_url)

# ===============================
# SPLASH PAGE
# ===============================
@app.route('/')
def home():
    return render_template('splash.html')

# Master code override
@app.route('/9999')
def master_override():
    session['authenticated'] = True
    return redirect(url_for('index'))

# Twilio send code
@app.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    phone = data.get("phone")
    if not phone:
        return jsonify({"error": "Phone required"}), 400

    # Generate a simple 4-digit code
    code = "1234"  # For simplicity; replace with random if needed
    session['twilio_code'] = code

    if twilio_client:
        try:
            twilio_client.messages.create(
                body=f"Your Beer Dollars code: {code}",
                from_=TWILIO_FROM,
                to=phone
            )
        except Exception as e:
            print(f"Twilio Error: {e}")

    print(f"Code sent to {phone}: {code}")  # For dev/debug
    return jsonify({"status": "sent"})

# Verify code or master
@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.get_json()
    code = data.get("code", "")

    if code in ["9999", "0000"] or code == session.get("twilio_code"):
        session['authenticated'] = True
        return jsonify({"success": True, "override": code in ["9999","0000"]})
    return jsonify({"success": False})

# ===============================
# INDEX PAGE
# ===============================
@app.route('/index')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('home'))

    return render_template(
        'index.html',
        GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY
    )

# ===============================
# API ROUTES
# ===============================
@app.route('/api/specials', methods=['GET'])
def get_specials():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, address, deal, day, lat, lng FROM specials")
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
                return jsonify(results)
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify([]), 500

@app.route('/api/add_special', methods=['POST'])
def add_special():
    try:
        data = request.get_json()
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO specials (name, address, deal, day, lat, lng)
                    VALUES (%s,%s,%s,%s,%s,%s)
                """, (data.get('name'), data.get('address'), data.get('deal'),
                      data.get('day'), data.get('lat'), data.get('lng')))
                conn.commit()
        return jsonify({"status":"success"}), 201
    except Exception as e:
        print(f"Insert Error: {e}")
        return jsonify({"error":"failed"}), 500

# ===============================
# RUN
# ===============================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
