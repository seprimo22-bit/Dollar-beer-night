from flask import Flask, render_template, jsonify, request
import os
import psycopg2
import psycopg2.extras
import json

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://beer_dollars_db_user:vbldLdTI705VOj3B1e4IphF7X9GK3pZw@dpg-d6e37ipr0fns73d6scc0-a/beer_dollars_db")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-bars")
def get_bars():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT bar_name AS bar, lat, lng, deals FROM bars")
        bars = cur.fetchall()
        for bar in bars:
            if isinstance(bar['deals'], str):
                bar['deals'] = json.loads(bar['deals'])
        cur.close()
        conn.close()
        return jsonify(bars)
    except Exception as e:
        print("Error fetching bars:", e)
        return jsonify([]), 500

@app.route("/add-bar", methods=["POST"])
def add_bar():
    data = request.get_json()
    required_fields = ["bar", "lat", "lng", "deals"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO bars (bar_name, lat, lng, deals) VALUES (%s,%s,%s,%s)",
            (data['bar'], data['lat'], data['lng'], json.dumps(data['deals']))
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        print("Error adding bar:", e)
        return jsonify({"error": "Database error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
