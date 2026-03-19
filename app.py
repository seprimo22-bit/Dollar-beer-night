from flask import Flask, render_template, request, jsonify
from config import Config
from models import db, Bar
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])

@app.route("/api/bars/<day>")
def get_bars(day):
    bars = Bar.query.filter_by(day=day).all()
    result = []
    for bar in bars:
        result.append({
            "id": bar.id,
            "name": bar.name,
            "address": bar.address,
            "deal": bar.deal,
            "day": bar.day,
            "lat": bar.lat,
            "lng": bar.lng,
            "paid": bar.paid
        })
    return jsonify(result)

@app.route("/api/add_bar", methods=["POST"])
def add_bar():
    data = request.get_json()
    bar = Bar(
        name=data.get("name"),
        address=data.get("address"),
        deal=data.get("deal"),
        day=data.get("day"),
        lat=data.get("lat"),
        lng=data.get("lng"),
        paid=data.get("paid", False)
    )
    db.session.add(bar)
    db.session.commit()
    return jsonify({"status": "success", "id": bar.id})

if __name__ == "__main__":
    app.run(debug=True)
