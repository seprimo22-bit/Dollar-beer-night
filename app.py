import os
from flask import Flask, render_template, session, redirect, url_for, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "brick_truth_99")

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL")

# ===============================
# DATABASE CONNECTION (optional)
# ===============================
def get_db_connection():
    if not DATABASE_URL:
        return None  # fallback to mock
    conn_url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    import psycopg
    return psycopg.connect(conn_url)

# ===============================
# ROUTES
# ===============================
@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/verify_code', methods=['POST'])
def verify_code():
    data = request.get_json()
    code = data.get("code")

    # Master override
    if code == "9999" or code.lower() == "master":
        session['authenticated'] = True
        return jsonify({"success": True, "override": True})

    # Phone verification logic placeholder
    # In real Twilio, you'd check code against sent code
    if code == "0000":  # temporary test code
        session['authenticated'] = True
        return jsonify({"success": True, "override": False})

    return jsonify({"success": False})

@app.route('/index')
def index():
    if not session.get('authenticated'):
        return redirect(url_for('splash'))
    return render_template('index.html', GOOGLE_MAPS_API_KEY=GOOGLE_MAPS_API_KEY)

# ===============================
# API ROUTES
# ===============================
@app.route('/api/specials', methods=['GET'])
def get_specials():
    # Try DB first
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT name,address,deal,day,lat,lng FROM specials")
                columns = [desc[0] for desc in cur.description]
                return jsonify([dict(zip(columns, row)) for row in cur.fetchall()])
        except Exception as e:
            print(f"DB error: {e}")
    # Fallback mock data
    return jsonify([
        {"name":"Test Bar","address":"123 Main St","deal":"$2 beers","day":"Monday","lat":41.101,"lng":-80.649},
        {"name":"Sample Pub","address":"456 Elm St","deal":"Half-price wings","day":"Tuesday","lat":41.103,"lng":-80.647},
        {"name":"Local Tap","address":"789 Oak St","deal":"Buy 1 get 1","day":"Friday","lat":41.102,"lng":-80.650}
    ])

@app.route('/api/add_special', methods=['POST'])
def add_special():
    data = request.get_json()
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO specials (name,address,deal,day,lat,lng) VALUES (%s,%s,%s,%s,%s,%s)",
                    (data.get("name"), data.get("address"), data.get("deal"), data.get("day"),
                     data.get("lat"), data.get("lng"))
                )
                conn.commit()
            return jsonify({"status":"success"}), 201
        except Exception as e:
            print(f"Insert Error: {e}")
            return jsonify({"status":"fail"}), 500
    else:
        print("Mock add_special:", data)
        return jsonify({"status":"success"}), 201

# ===============================
# RUN
# ===============================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
