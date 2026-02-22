from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------
# Database Model
# ------------------------
class Special(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bar_name = db.Column(db.String(100), nullable=False)
    deal = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------------
# Routes
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add_special", methods=["POST"])
def add_special():
    data = request.json

    special = Special(
        bar_name=data["bar_name"],
        deal=data["deal"],
        day=data["day"],
        latitude=data.get("latitude"),
        longitude=data.get("longitude")
    )

    db.session.add(special)
    db.session.commit()

    return jsonify({"status": "success"})

@app.route("/get_specials/<day>")
def get_specials(day):
    specials = Special.query.filter_by(day=day).all()

    results = []
    for s in specials:
        results.append({
            "bar_name": s.bar_name,
            "deal": s.deal,
            "latitude": s.latitude,
            "longitude": s.longitude
        })

    return jsonify(results)

# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
