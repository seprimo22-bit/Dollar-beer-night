from flask import Flask, render_template, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'beer_dollars_secret_1616')

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    special = db.Column(db.String(250))
    day = db.Column(db.String(20)) # Monday, Tuesday, etc.

def get_effective_day():
    """Logic to handle bar time (day changes at 2:30 AM)"""
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        return (now - timedelta(days=1)).strftime('%A')
    return now.strftime('%A')

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/main')
def index():
    if not session.get('authorized'):
        return render_template('splash.html')
    return render_template('index.html')

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    code = data.get('code')
    # MASTER BYPASS CODES
    if code in ["1616", "0000", "9999"]:
        session['authorized'] = True
        return jsonify({"status": "success"})
    # Normal Twilio logic would go here
    return jsonify({"error": "Invalid code"}), 401

@app.route('/api/specials', methods=['GET'])
def get_specials():
    day = request.args.get('day', get_effective_day())
    bars = Bar.query.filter_by(day=day).all()
    return jsonify([{
        'name': b.name, 'address': b.address,
        'lat': b.lat, 'lng': b.lng, 'special': b.special
    } for b in bars])

@app.route('/api/add-bar', methods=['POST'])
def add_bar():
    data = request.json
    new_bar = Bar(
        name=data['name'], address=data['address'],
        lat=data['lat'], lng=data['lng'],
        special=data['special'], day=data['day']
    )
    db.session.add(new_bar)
    db.session.commit()
    return jsonify({"status": "added"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
