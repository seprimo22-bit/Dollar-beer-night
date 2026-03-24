import os
import random
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import psycopg
from twilio.rest import Client

# 1. Initialize Environment
load_dotenv()

app = Flask(__name__)
# Secure the session
app.secret_key = os.getenv("FLASK_SECRET_KEY", "brick_truth_99") 

# 2. Config & Credentials 
# CALLED EXACTLY AS IN RENDER: GOOGLE_MAPS_API_KEY
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") 
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_VERIFY_SERVICE = os.getenv("TWILIO_VERIFY_SERVICE_SID")
DATABASE_URL = os.getenv("DATABASE_URL")

# --- DATABASE CONNECTION HELPER ---
def get_db_connection():
    """
    Render provides 'postgres://', but psycopg3 REQUIRES 'postgresql://'.
    This fix prevents the 500 error on DB connection.
    """
    if not DATABASE_URL:
        return None
    
    conn_url = DATABASE_URL
    if conn_url.startswith("postgres://"):
        conn_url = conn_url.replace("postgres://", "postgresql://", 1)
    
    return psycopg.connect(conn_url)

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.json
    phone = data.get('phone')
    code = data.get('code')
    
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        verification_check = client.verify \
            .v2 \
            .services(TWILIO_VERIFY_SERVICE) \
            .verification_checks \
            .create(to=phone, code=code)

        if verification_check.status == 'approved':
            session['authenticated'] = True
            return jsonify({"success": True, "redirect": url_for('index')})
        else:
            return jsonify({"success": False, "error": "Invalid Code"}), 401
    except Exception as e:
        print(f"Twilio Error: {e}")
        return jsonify({"success": False, "error": "SMS Verification Failed"}), 500

@app.route('/index')
def index():
    """
    The main map page.
    Passes GOOGLE_MAPS_API_KEY to the index.html.
    """
    if not session.get('authenticated'):
        return redirect(url_for('home'))
        
    # PASSING THE EXACT KEY NAME
    return render_template('index.html', GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)

# --- API ENDPOINTS ---

@app.route('/api/specials', methods=['GET'])
def get_specials():
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT name, address, deal, day, lat, lng FROM specials")
            columns = [desc[0] for desc in cur.description]
            results = [dict(zip(columns, row)) for row in cur.fetchall()]
            return jsonify(results)
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify([]), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
