import os
import math
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import googlemaps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'brick_1_percent_anchor')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_API_KEY'))

# --- THE MODELS (Lined up with your code) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(32), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

# --- THE LOGIC ---
@app.route('/')
def index():
    return render_template('index.html', google_key=os.environ.get('GOOGLE_MAPS_API_KEY'))

@app.route('/api/add', methods=['POST'])
def add_bar():
    data = request.json
    # Geocode logic using the new specific fields
    full_address = f"{data['address']}, {data['city']}, {data['state']} {data['zip_code']}"
    g = gmaps.geocode(full_address)
    lat, lng = (g[0]['geometry']['location']['lat'], g[0]['geometry']['location']['lng']) if g else (0,0)
    
    new_bar = Bar(
        name=data['name'], address=data['address'], city=data['city'],
        state=data['state'], zip_code=data['zip_code'], deal=data['deal'],
        day_of_week=data['day_of_week'].lower(), lat=lat, lng=lng
    )
    db.session.add(new_bar)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/api/bars', methods=['GET'])
def get_bars():
    today = datetime.now().strftime('%A').lower()
    bars = Bar.query.filter_by(day_of_week=today).all()
    return jsonify([{
        "id": b.id, "name": b.name, "deal": b.deal, "address": b.address,
        "city": b.city, "lat": b.lat, "lng": b.lng
    } for b in bars])

if __name__ == '__main__':
    with app.app_context():
        # db.drop_all() # Uncomment this once to wipe the old "broken" table structure
        db.create_all()
    app.run()
    
