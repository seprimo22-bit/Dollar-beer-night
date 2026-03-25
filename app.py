import os
from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from dotenv import load_dotenv
import psycopg

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "brick_truth_99")

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# ===============================
# DATABASE CONNECTION
# ===============================
def get_db_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL is not set")
    conn_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return psycopg.connect(conn_url)

# ===============================
# ROUTES
# ===============================
@app.route('/')
def home():
    return render_template('splash.html')

# Master code override (9999)
@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.get_json()
    code = data.get("code", "")
    if code == "9999" or code == "0000":  # Master codes
        session['authenticated'] = True
        return jsonify({"success": True, "override": True})
    # Here you could add real Twilio verification logic
    return jsonify({"success": False})

@app.route('/index')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('home'))
    return render_template('index.html', GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)

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
        print(f"Database Error: {e}")
        return jsonify([]), 500

@app.route('/api/add_special', methods=['POST'])
def add_special():
    try:
        data = request.get_json()
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO specials (name, address, deal, day, lat, lng)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    data.get('name'),
                    data.get('address'),
                    data.get('deal'),
                    data.get('day'),
                    data.get('lat'),
                    data.get('lng')
                ))
                conn.commit()
        return jsonify({"status": "success"}), 201
    except Exception as e:
        print(f"Insert Error: {e}")
        return jsonify({"error": "failed"}), 500

# ===============================
# RUN
# ===============================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
