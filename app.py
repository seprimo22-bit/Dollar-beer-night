import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
# Import the extra tools your logs show you are using
import psycopg 
from twilio.rest import Client

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_key_123") # Required for session/redirects

# --- YOUR CORE CONFIG ---
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Log check for Render
if not GOOGLE_MAPS_KEY:
    print("❌ ERROR: GOOGLE_MAPS_KEY is missing!")
else:
    print("✅ GOOGLE_MAPS_KEY detected.")

# --- ROUTES ---

@app.route('/')
def root():
    # If your app starts with a login/verification, keep that logic here
    return render_template('login.html') 

@app.route('/verify_code', methods=['POST'])
def verify_code():
    # Keep your existing logic that checks the SMS code
    # Assuming successful verification leads to /index:
    return jsonify({"success": True, "redirect": "/index"})

@app.route('/index')
def index():
    """
    THIS IS THE CRITICAL FIX. 
    It ensures when you get to the main app, the Map Key is passed.
    """
    return render_template('index.html', GOOGLE_MAPS_KEY=GOOGLE_MAPS_KEY)

# --- API ENDPOINTS FOR THE MAP ---

@app.route('/api/specials', methods=['GET'])
def get_specials():
    # This pulls the 'specials' for your JS to put on the map
    # You can link this to your Postgres DB here
    return jsonify([]) 

@app.route('/api/add_special', methods=['POST'])
def add_special():
    data = request.json
    # Your logic to save the new special to the database
    print(f"Saving to DB: {data}")
    return jsonify({"success": True})

if __name__ == '__main__':
    # Use port 10000 for Render compatibility if running locally
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
    
