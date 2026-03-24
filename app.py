import os
from flask import Flask, render_template, session, redirect, url_for, jsonify
from dotenv import load_dotenv
import psycopg

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "brick_truth_99")

# THIS IS THE EXACT VARIABLE: GOOGLE_MAPS_API_KEY
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        return None
    # Fix for Render's postgres string
    conn_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return psycopg.connect(conn_url)

@app.route('/')
def home():
    # Calling splash.html as seen in your templates folder
    return render_template('splash.html')

@app.route('/index')
def index():
    # Pass the ALL CAPS variable to the template
    return render_template('index.html', GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
