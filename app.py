import os
from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Database connection (Render)
DB_URL = os.getenv('RENDER_DB_URL', 'dpg-d6e37ipr0fns73d6scc0-a')

def get_db_connection():
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    return conn

# --- Routes ---

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/index')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bars;")
    bars = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', bars=bars)

@app.route('/admin')
def admin():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bars ORDER BY id DESC;")
    bars = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', bars=bars)

@app.route('/add_bar', methods=['POST'])
def add_bar():
    data = request.get_json()
    name = data.get('name')
    lat = data.get('lat')
    lng = data.get('lng')
    description = data.get('description')
    verified = False

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO bars (name, lat, lng, description, verified) VALUES (%s,%s,%s,%s,%s)",
        (name, lat, lng, description, verified)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/verify_bar/<int:bar_id>', methods=['POST'])
def verify_bar(bar_id):
    code = request.json.get('code')
    if code == '1616':
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE bars SET verified = TRUE WHERE id = %s", (bar_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'status': 'verified'})
    else:
        return jsonify({'status': 'failed'}), 403

if __name__ == '__main__':
    app.run(debug=True)
