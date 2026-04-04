from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from twilio.rest import Client
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'beer_dollars_999_super_secret')

# -----------------------
# MASTER ADMIN CODES
# -----------------------
MASTER_CODES = ['999', '1616', '999-000']

# -----------------------
# DATABASE CONNECTION
# -----------------------
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

# -----------------------
# INIT DB
# -----------------------
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

init_db()

# -----------------------
# SMART BUSINESS DAY (2:30 AM rule)
# -----------------------
def get_business_day():
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        now -= timedelta(days=1)
    return now.strftime('%A')

# -----------------------
# ROUTES
# -----------------------
@app.route('/', methods=['GET'])
def splash():
    return render_template('splash.html')

@app.route('/main')
def main():
    if not session.get('authorized'):
        return redirect(url_for('splash'))
    current_day = get_business_day()
    return render_template('index.html', current_day=current_day)

# -----------------------
# API: FETCH SPECIALS
# -----------------------
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

# -----------------------
# API: ADD SPECIAL
# -----------------------
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

# -----------------------
# TWILIO LOGIN FLOW
# -----------------------
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
generated_codes = {}

@app.route('/api/send-code', methods=['POST'])
def send_code():
    phone = request.json.get('phone')
    code = str(random.randint(100000, 999999))
    generated_codes[phone] = code
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=f"Your Beer Dollars login code is: {code}",
            from_=TWILIO_PHONE_NUMBER,
            to=phone
        )
        return jsonify({"status": "Code sent!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    phone = request.json.get('phone')
    code = request.json.get('code')

    if code in MASTER_CODES or generated_codes.get(phone) == code:
        session['authorized'] = True
        return jsonify({"status": "success"})
    
    return jsonify({"error": "Invalid code"}), 401

# -----------------------
# RUN
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
