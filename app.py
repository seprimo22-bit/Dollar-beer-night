from flask import Flask, render_template, jsonify
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# DATABASE CONFIG (replace with environment variable for security in Render)
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://beer_dollars_db_user:vbldLdTI705VOj3B1e4IphF7X9GK3pZw@dpg-d6e37ipr0fns73d6scc0-a/beer_dollars_db")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-bars")
def get_bars():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # Assumes table "bars" with columns: bar_name, lat, lng, deals JSON
        cur.execute("SELECT bar_name AS bar, lat, lng, deals FROM bars")
        bars = cur.fetchall()
        # Convert JSON field if necessary
        for bar in bars:
            if isinstance(bar['deals'], str):
                import json
                bar['deals'] = json.loads(bar['deals'])
        cur.close()
        conn.close()
        return jsonify(bars)
    except Exception as e:
        print("Error fetching bars:", e)
        return jsonify([]), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
