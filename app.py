import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
import psycopg

# 1. Initialize Environment
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "brick_truth_99") 

# EXACT VARIABLE NAME FROM YOUR RENDER ENVIRONMENT
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# --- DATABASE CONNECTION HELPER ---
def get_db_connection():
    """Fixes the 'postgres://' vs 'postgresql://' issue on Render."""
    if not DATABASE_URL:
        return None
    conn_url = DATABASE_URL
    if conn_url.startswith("postgres://"):
        conn_url = conn_url.replace("postgres://", "postgresql://", 1)
    return psycopg.connect(conn_url)

# --- ROUTES ---

@app.route('/')
def home():
    """Loads the splash page identified in your templates folder."""
    return render_template('splash.html')

@app.route('/index')
def index():
    """The main map page. Passes the verified GOOGLE_MAPS_API_KEY."""
    # Simple auth check for the session
    if not session.get('authenticated'):
        # For testing, you can comment the redirect out, or ensure login sets this to True
        # session['authenticated'] = True 
        return redirect(url_for('home'))
        
    return render_template('index.html', GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)

# --- API ENDPOINTS ---

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
        print(f"Database Error: {e}")
        return jsonify([]), 500

@app.route('/api/add_special', methods=['POST'])
def add_special():
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
