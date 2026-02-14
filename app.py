from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

# -------- DATABASE INIT --------
def init_db():
    conn = sqlite3.connect("specials.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS specials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bar TEXT,
            price TEXT,
            day TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -------- SIMPLE UI --------
HTML = """
<h1>Dollar Beer Night</h1>

<form method="POST" action="/add">
    Bar: <input name="bar"><br>
    Price: <input name="price"><br>
    Day: <input name="day"><br>
    Notes: <input name="notes"><br>
    <button type="submit">Add Special</button>
</form>

<hr>

<a href="/list">View Specials</a>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

# -------- ADD SPECIAL --------
@app.route("/add", methods=["POST"])
def add():
    data = request.form
    conn = sqlite3.connect("specials.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO specials (bar, price, day, notes) VALUES (?, ?, ?, ?)",
        (data["bar"], data["price"], data["day"], data["notes"])
    )
    conn.commit()
    conn.close()
    return "Added!"

# -------- LIST SPECIALS --------
@app.route("/list")
def list_specials():
    conn = sqlite3.connect("specials.db")
    c = conn.cursor()
    rows = c.execute("SELECT * FROM specials").fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
