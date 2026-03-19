from flask import Flask, render_template, request, jsonify
from config import Config
from models import db, Bar
import os

# --- FLASK APP SETUP ---
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# --- CREATE DATABASE TABLES ---
@app.before_first_request
def create_tables():
    db.create_all()

# --- ROUTES ---

# Index page
@app.route("/")
def index():
    return render_template("index.html", google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"])

# Admin page
@app.route("/admin")
def admin():
    return render_template("admin.html")

# Get bars for a specific day
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

# Add a new bar
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

# Delete a bar
@app.route("/api/delete_bar/<int:bar_id>", methods=["DELETE"])
def delete_bar(bar_id):
    bar = Bar.query.get(bar_id)
    if bar:
        db.session.delete(bar)
        db.session.commit()
        return jsonify({"status":"deleted"})
    return jsonify({"status":"not found"}), 404

# --- RUN APP ---
if __name__ == "__main__":
    app.run(debug=True)
