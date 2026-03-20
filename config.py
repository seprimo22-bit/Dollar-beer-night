
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime
import math
import googlemaps

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
gmaps = googlemaps.Client(key=app.config['GOOGLE_MAPS_API_KEY'])

class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    deal = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

def get_dist(lat1, lon1, lat2, lon2):
    R = 3958.8 
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

@app.route('/')
def index():
    return render_template('index.html', google_key=app.config['GOOGLE_MAPS_API_KEY'])

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/verify', methods=['POST'])
def verify():
    if request.json.get('code') == '0000':
        session['verified'] = True
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route('/api/bars', methods=['GET'])
def get_bars():
    today = datetime.now().strftime('%A')
    u_lat, u_lng = request.args.get('lat', type=float), request.args.get('lng', type=float)
    bars = Bar.query.filter_by(day=today).all()
    res = []
    for b in bars:
        d = get_dist(u_lat, u_lng, b.lat, b.lng) if u_lat else None
        if d is None or d <= 40:
            res.append({"id": b.id, "name": b.name, "deal": b.deal, "address": b.address, "lat": b.lat, "lng": b.lng, "dist": round(d, 1) if d else None})
    return jsonify(sorted(res, key=lambda x: x['dist'] or 999))

@app.route('/api/add', methods=['POST'])
def add_bar():
    data = request.json
    lat, lng = data.get('lat'), data.get('lng')
    if not lat:
        g = gmaps.geocode(data['address'])
        if g: lat, lng = g[0]['geometry']['location']['lat'], g[0]['geometry']['location']['lng']
    db.session.add(Bar(name=data['name'], address=data['address'], deal=data['deal'], day=data['day'], lat=lat, lng=lng))
    db.session.commit()
    return jsonify({"success": True})

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run()
