import os
import math
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import googlemaps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'brick_1_percent_anchor')
# Fix for Render/Postgres connection string
db_url = os.environ.get("DATABASE_URL", "sqlite:///beer_dollars.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_API_KEY'))

# --- MODELS (Matched to your verified models.py) ---
class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(128))
    state = db.Column(db.String(64))
    zip_code = db.Column(db.String(32))
    deal = db.Column(db.String(256), nullable=False)
    day_of_week = db.Column(db.String(16), nullable=False) 
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html', google_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    if data.get('code') == '0000':
        session['verified'] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/api/bars', methods=['GET'])
def get_bars():
    today = datetime.now().strftime('%A').lower()
    bars = Bar.query.filter_by(day_of_week=today).all()
    u_lat = request.args.get('lat', type=float)
    u_lng = request.args.get('lng', type=float)
    
    res = []
    for b in bars:
        dist = None
        if u_lat and u_lng:
            # Haversine Formula for the 40-mile radius
            R = 3958.8
            dlat, dlon = math.radians(b.lat-u_lat), math.radians(b.lng-u_lng)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(u_lat)) * math.cos(math.radians(b.lat)) * math.sin(dlon/2)**2
            dist = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        if dist is None or dist <= 40:
            res.append({
                "id": b.id, "name": b.name, "deal": b.deal, "address": b.address,
                "lat": b.lat, "lng": b.lng, "dist": round(dist, 1) if dist else "N/A"
            })
    return jsonify(sorted(res, key=lambda x: x.get('dist') if isinstance(x.get('dist'), float) else 999))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
    
