import os
import random
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import psycopg
from twilio.rest import Client

# 1. Initialize Environment
load_dotenv()

app = Flask(__name__)
# Secure the session for your redirect logic
app.secret_key = os.getenv("FLASK_SECRET_KEY", "brick_truth_secret_99") 

# 2. Config & Credentials
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE = os.getenv("TWILIO_VERIFY_SERVICE_SID")
DATABASE_URL = os.getenv("DATABASE_URL")

# Log verification for the Render console
if not GOOGLE_MAPS_KEY:
    print("⚠️ WARNING: GOOGLE_MAPS_KEY is missing from environment!")

# --- DATABASE CONNECTION HELPER ---
def get_db_connection():
    return psycopg.connect(DATABASE_URL)

# --- ROUTES ---

@app.route('/')
def home():
    """Initial landing page - likely your login/SMS entry."""
    return render_template('login.html')

@app.route('/verify_code', methods=['POST'])
def verify_code():
    """
    Handles the Paper Zero pipeline verification.
    Once the user is 'Sovereign', we push them to the map.
    """
    data = request.json
    phone = data.get('phone')
    code = data.get('code')
    
    # Twilio Verification Logic
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        verification_check = client.verify \
            .v2 \
            .services(TWILIO_VERIFY_SERVICE) \
            .verification_checks \
            .create(to=phone, code=code)

        if verification_check.status == 'approved':
            session['authenticated'] = True
            session['user_phone'] = phone
            return jsonify({"success": True, "redirect": url_for('index')})
        else:
            return jsonify({"success": False, "error": "Invalid Code"}), 401
    except Exception as e:
        print(f"Verification Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/index')
def index():
    """
    The Money Maker UI. 
    Crucial: Passes the API key so the Map actually turns on.
    """
    # Security check: Ensure they passed the pipeline
    if not session.get('authenticated'):
        return redirect(url_for('home'))
        
    return render_template('index.html', GOOGLE_MAPS_KEY=GOOGLE_MAPS_KEY)

# --- API ENDPOINTS (The Data Feed) ---

@app.route('/api/specials', methods=['GET'])
def get_specials():
    """Fetches the beer deals from your Postgres DB."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, address, deal, day, lat, lng FROM specials")
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
                return jsonify(results)
    except Exception as e:
        print(f"DB Fetch Error: {e}")
        return jsonify([]), 500

@app.route('/api/add_special', methods=['POST'])
def add_special():
    """Saves a new deal to the pipeline."""
    data = request.json
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO specials (name, address, deal, day, lat, lng) VALUES (%s, %s, %s, %s, %s, %s)",
                    (data['name'], data['address'], data['deal'], data['day'], data['lat'], data['lng'])
                )
            conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Use Render's dynamic port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
