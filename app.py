from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
import os
from datetime import datetime, timedelta

app = Flask(__name__)
# Pulls the secret key you set in Render env
app.secret_key = os.environ.get('SECRET_KEY', 'beer_dollars_secret_1616')

# DATABASE CONNECTION: Handles Render's postgres prefix
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TWILIO SETUP: Pulls from Render Environment Variables
TWILIO_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = os.environ.get('TWILIO_PHONE_NUMBER')

class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    special = db.Column(db.String(250))
    day = db.Column(db.String(20))

# LOGIN LOGIC & OVERRIDES
@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    data = request.json
    code = data.get('code')
    # Master Overrides
    if code in ['0000', '1616', '9999']:
        session['logged_in'] = True
        return jsonify({"status": "success"}), 200
    
    # Optional: Twilio verification logic can go here if needed later
    return jsonify({"status": "invalid"}), 401

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/main')
def main_app():
    if not session.get('logged_in'):
        return redirect(url_for('splash'))
    return render_template('index.html')

@app.route('/api/add-bar', methods=['POST'])
def add_bar():
    data = request.json
    try:
        new_bar = Bar(
            name=data['name'], address=data['address'],
            lat=data['lat'], lng=data['lng'],
            special=data['special'], day=data['day']
        )
        db.session.add(new_bar)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/specials')
def get_specials():
    # Day Logic: Before 2:30 AM shows "yesterday"
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        query_day = (now - timedelta(days=1)).strftime('%A')
    else:
        query_day = request.args.get('day', now.strftime('%A'))
        
    bars = Bar.query.filter_by(day=query_day).all()
    return jsonify([{
        'name': b.name, 'address': b.address, 
        'lat': b.lat, 'lng': b.lng, 'special': b.special
    } for b in bars])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
