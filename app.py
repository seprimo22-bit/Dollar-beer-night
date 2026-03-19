from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__, static_folder="static", static_url_path="/static")

# DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///beer.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# MODEL
class Special(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bar_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200))
    deal = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

with app.app_context():
    db.create_all()

# GEOCODER
def geocode(query):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 1}
        r = requests.get(url, params=params, headers={"User-Agent": "BeerDollarsApp"}, timeout=5)
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print("Geocode error:", e)
    return None, None

# HOME
@app.route("/")
def home():
    return render_template("index.html")

# ADD SPECIAL
@app.route("/add_special", methods=["POST"])
def add_special():
    data = request.json
    bar = data.get("bar_name", "")
    address = data.get("address", "")
    deal = data.get("deal", "")
    day = data.get("day", "").capitalize()

    if not bar or not deal or not day:
        return jsonify(success=False)

    queries = [f"{bar} {address}", f"{bar} near {address}", address, bar]
    lat, lng = None, None
    for q in queries:
        lat, lng = geocode(q)
        if lat:
            break

    special = Special(bar_name=bar, address=address, deal=deal, day=day, latitude=lat, longitude=lng)
    db.session.add(special)
    db.session.commit()

    return jsonify(success=True)

# GET BY DAY
@app.route("/get_specials/<day>")
def get_specials(day):
    specials = Special.query.filter_by(day=day.capitalize()).all()
    return jsonify([
        {"id": s.id, "bar_name": s.bar_name, "deal": s.deal, "lat": s.latitude, "lng": s.longitude}
        for s in specials
    ])

if __name__ == "__main__":
    app.run(debug=True)
# ADMIN PANEL
@app.route("/admin")
def admin_panel():
    specials = Special.query.all()
    return render_template("admin.html", specials=specials)
# EDIT SPECIAL
@app.route("/edit_special/<int:special_id>", methods=["POST"])
def edit_special(special_id):
    special = Special.query.get_or_404(special_id)
    special.bar_name = request.form.get("bar_name", special.bar_name)
    special.address = request.form.get("address", special.address)
    special.deal = request.form.get("deal", special.deal)
    special.day = request.form.get("day", special.day)

    # Update geocode if address changed
    if special.address:
        lat, lng = geocode(f"{special.bar_name} {special.address}")
        special.latitude = lat
        special.longitude = lng

    db.session.commit()
    return render_template("admin.html", specials=Special.query.all())

# DELETE SPECIAL
@app.route("/delete_special/<int:special_id>", methods=["POST"])
def delete_special(special_id):
    special = Special.query.get_or_404(special_id)
    db.session.delete(special)
    db.session.commit()
    return render_template("admin.html", specials=Special.query.all())
