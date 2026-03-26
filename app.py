from flask import Flask, jsonify, render_template
import psycopg2

app = Flask(__name__)

# PostgreSQL connection
DB_URL = "postgresql://beer_dollars_db_user:vbldLdTI705VOj3B1e4IphF7X9GK3pZw@dpg-d6e37ipr0fns73d6scc0-a/beer_dollars_db"

def get_connection():
    return psycopg2.connect(DB_URL)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-bars")
def get_bars():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT bar_name, latitude, longitude, thursday_deal, friday_deal, saturday_deal
            FROM bars;
        """)
        bars = []
        for row in cur.fetchall():
            bars.append({
                "bar": row[0],
                "lat": float(row[1]),
                "lng": float(row[2]),
                "deals": {
                    "Thursday": row[3],
                    "Friday": row[4],
                    "Saturday": row[5]
                }
            })
        cur.close()
        conn.close()
        return jsonify(bars)
    except Exception as e:
        print("DB error:", e)
        return jsonify([]), 500

if __name__ == "__main__":
    app.run(debug=True)
