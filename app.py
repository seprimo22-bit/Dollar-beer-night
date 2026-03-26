
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")

# Database setup (SQLite for MVP)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beerdollars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    day = db.Column(db.String(10), nullable=False)  # Monday, Tuesday, etc.
    special = db.Column(db.String(100), nullable=False)

# Initialize database
with app.app_context():
    db.create_all()

# Master codes
MASTER_CODES = ["999-000", "1616"]

# Splash page
@app.route("/", methods=["GET", "POST"])
def splash():
    if request.method == "POST":
        phone = request.form.get("phone")
        code = request.form.get("code")
        if code in MASTER_CODES:
            session['authorized'] = True
            return redirect(url_for("main"))
        else:
            return render_template("splash.html", error="Invalid code")
    return render_template("splash.html")

# Main app page
@app.route("/main")
def main():
    if not session.get("authorized"):
        return redirect(url_for("splash"))
    return render_template("index.html")

# API: Get bars (optionally by day)
@app.route("/api/bars")
def get_bars():
    day = request.args.get("day")
    query = Bar.query
    if day:
        query = query.filter_by(day=day)
    bars = query.all()
    bars_list = [
        {
            "id": bar.id,
            "name": bar.name,
            "address": bar.address,
            "latitude": bar.latitude,
            "longitude": bar.longitude,
            "day": bar.day,
            "special": bar.special
        } for bar in bars
    ]
    return jsonify(bars_list)

# API: Add new bar
@app.route("/api/bars/add", methods=["POST"])
def add_bar():
    data = request.json
    try:
        bar = Bar(
            name=data['name'],
            address=data['address'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            day=data['day'],
            special=data['special']
        )
        db.session.add(bar)
        db.session.commit()
        return jsonify({"status": "success", "id": bar.id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
