from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'beer_dollars_secret_1616')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

MASTER_CODES = ['1616', '999', '0000']  # any code you want

# ---------------- DATABASE ----------------
def get_db_connection():
    url = os.environ.get('DATABASE_URL')
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bars (
            id SERIAL PRIMARY KEY,
            name TEXT,
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

init_db()

# ---------------- ROUTES ----------------
@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/main')
def main():
    if not session.get('authorized'):
        return redirect('/')
    return render_template('index.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    code = data.get('code')

    if code in MASTER_CODES:
        session['authorized'] = True
        return jsonify({"success": True})
    
    return jsonify({"success": False}), 401

# ---------------- API ----------------
@app.route('/api/specials')
def get_specials():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM bars")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

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
        data['name'], data['address'], data['special'], data['day'],
        data['lat'], data['lng'], False
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
