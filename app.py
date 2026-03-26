import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from twilio.rest import Client

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://beer_dollars_db_user:password@localhost/beer_dollars_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Twilio placeholders
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID else None

MASTER_CODES = ["999000", "1616"]

# Models
class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    specials = db.Column(db.JSON)  # {"Monday": "$2 beers", "Tuesday": ...}

# Routes
@app.route('/')
def index():
    return render_template('index.html', google_maps_key=os.environ.get('GOOGLE_MAPS_KEY'))

# API: Get bars filtered by day
@app.route('/api/bars', methods=['GET'])
def get_bars():
    day = request.args.get('day')
    bars = Bar.query.all()
    bars_list = []
    for bar in bars:
        bars_list.append({
            "id": bar.id,
            "name": bar.name,
            "address": bar.address,
            "lat": bar.lat,
            "lng": bar.lng,
            "special": bar.specials.get(day, None) if day else None
        })
    return jsonify(bars_list)

# API: Add bar
@app.route('/api/bars', methods=['POST'])
def add_bar():
    data = request.json
    if not data.get('name') or not data.get('address') or not data.get('specials'):
        return jsonify({"error": "Missing required fields"}), 400
    bar = Bar(
        name=data['name'],
        address=data['address'],
        lat=data.get('lat'),
        lng=data.get('lng'),
        specials=data['specials']
    )
    db.session.add(bar)
    db.session.commit()
    return jsonify({"success": True, "bar": {
        "id": bar.id,
        "name": bar.name,
        "address": bar.address,
        "lat": bar.lat,
        "lng": bar.lng,
        "specials": bar.specials
    }})

# Twilio Verification (basic example)
@app.route('/api/send_code', methods=['POST'])
def send_code():
    number = request.json.get('number')
    if number in MASTER_CODES:
        return jsonify({"success": True, "code": "MASTER"})
    code = "123456"  # Generate random code in production
    # if twilio_client:
    #     twilio_client.messages.create(
    #         body=f"Your Beer Dollars code is {code}",
    #         from_=TWILIO_NUMBER,
    #         to=number
    #     )
    return jsonify({"success": True, "code": code})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
