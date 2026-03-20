import os
import math
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import googlemaps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brick_1_percent_anchor'
# Render Postgres Fix
db_url = os.environ.get("DATABASE_URL", "sqlite:///beer_dollars.db")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_API_KEY'))

class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    deal = db.Column(db.String(256), nullable=False)
    day_of_week = db.Column(db.String(16), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html', google_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

@app.route('/api/bars', methods=['GET'])
def get_bars():
    today = datetime.now().strftime('%A').lower()
    u_lat = request.args.get('lat', type=float)
    u_lng = request.args.get('lng', type=float)
    bars = Bar.query.filter_by(day_of_week=today).all()
    res = []
    for b in bars:
        dist = 0
        if u_lat and u_lng:
            R = 3958.8
            dlat, dlon = math.radians(b.lat-u_lat), math.radians(b.lng-u_lng)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(u_lat)) * math.cos(math.radians(b.lat)) * math.sin(dlon/2)**2
            dist = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        if dist <= 40:
            res.append({"name": b.name, "deal": b.deal, "lat": b.lat, "lng": b.lng, "dist": round(dist, 1)})
    return jsonify(sorted(res, key=lambda x: x['dist']))

@app.route('/api/add', methods=['POST'])
def add_bar():
    data = request.json
    new_bar = Bar(
        name=data['name'], address="Pinned", deal=data['deal'],
        day_of_week="friday", lat=data['lat'], lng=data['lng']
    )
    db.session.add(new_bar)
    db.session.commit()
    return jsonify({"success": True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
