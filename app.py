from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'beer_dollars_999_super_secret')

# 1. Master Override Codes
MASTER_CODES = ['999', '1616', '999-000']

# 2. Database Connection Fix
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# 3. AUTO-BUILD THE TABLE (Runs every time the app starts)
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS bars (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                special TEXT,
                day TEXT,
                lat DOUBLE PRECISION,
                lng DOUBLE PRECISION,
                verified BOOLEAN DEFAULT FALSE
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Database Table Initialized Successfully")
    except Exception as e:
        print(f"Database Init Error: {e}")

# Call the init function immediately
init_db()

# 4. Smart Day Logic (The 2:30 AM Rule)
def get_business_day():
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        now -= timedelta(days=1)
    return now.strftime('%A')

# -------------------------
# ROUTES
# -------------------------

@app.route('/', methods=['GET', 'POST'])
def splash():
    if request.method == 'POST':
        code = request.form.get('code')
        if code in MASTER_CODES:
            session['authorized'] = True
            return redirect(url_for('main'))
    return render_template('splash.html')

@app.route('/main')
def main():
    if not session.get('authorized'):
        return redirect(url_for('splash'))
    current_day = get_business_day()
    return render_template('index.html', current_day=current_day)

@app.route('/api/specials', methods=['GET'])
def get_specials():
    day = request.args.get('day', get_business_day())
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM bars WHERE day = %s OR day = 'Daily'", (day,))
    specials = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(specials)

@app.route('/api/specials', methods=['POST'])
def add_special():
    if not session.get('authorized'):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bars (name, address, special, day, lat, lng, verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get('name'), 
        data.get('address'), 
        data.get('special'), 
        data.get('day'),
        data.get('lat', 0), 
        data.get('lng', 0),
        False 
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "added"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
