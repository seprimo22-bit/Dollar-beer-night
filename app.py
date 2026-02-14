from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, template_folder="templates")

DB = "specials.db"


# ---------------------------
# Database setup + seed data
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS specials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bar TEXT,
            price TEXT,
            day TEXT,
            notes TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed starter data if empty
    c.execute("SELECT COUNT(*) FROM specials")
    if c.fetchone()[0] == 0:
        c.executemany("""
            INSERT INTO specials (bar, price, day, notes)
            VALUES (?, ?, ?, ?)
        """, [
            ("Rusty Tap", "$1.00", "Friday", "College night"),
            ("Brick House Bar", "$1.50", "Saturday", "Local favorite"),
            ("Downtown Pub", "$1.25", "Thursday", "Happy hour special")
        ])

    conn.commit()
    conn.close()


init_db()


# ---------------------------
# Home page
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------
# Add special
# ---------------------------
@app.route("/add", methods=["POST"])
def add_special():
    bar = request.form.get("bar")
    price = request.form.get("price")
    day = request.form.get("day")
    notes = request.form.get("notes")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "INSERT INTO specials (bar, price, day, notes) VALUES (?, ?, ?, ?)",
        (bar, price, day, notes)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ---------------------------
# Get specials (today first)
# ---------------------------
@app.route("/specials")
def get_specials():
    today = datetime.now().strftime("%A")

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Today's specials first
    c.execute("""
        SELECT bar, price, day, notes
        FROM specials
        ORDER BY
            CASE WHEN LOWER(day) = LOWER(?) THEN 0 ELSE 1 END,
            created DESC
    """, (today,))

    results = c.fetchall()
    conn.close()

    return jsonify(results)


# ---------------------------
# Health check for Render
# ---------------------------
@app.route("/health")
def health():
    return "OK", 200


# ---------------------------
# Local testing only
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
