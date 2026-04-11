from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from twilio.rest import Client
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'beer_dollars_1616_override')

# 1. Database Connection (Using your Render URL)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 2. Twilio Setup (Using your Render Environment Variables)
TWILIO_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_SERVICE = os.environ.get('TWILIO_VERIFY_SERVICE_SID')

class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    special = db.Column(db.String(250))
    day = db.Column(db.String(20))

@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/main')
def index():
    if not session.get('authorized'):
        return redirect(url_for('splash'))
    return render_template('index.html')

@app.route('/api/verify-code', methods=['POST'])
def verify():
    data = request.json
    code = data.get('code')
    
    # MASTER OVERRIDE CHECK
    if code in ["1616", "0000", "9999"]:
        session['authorized'] = True
        return jsonify({"status": "success"})

    # TWILIO VERIFICATION
    if TWILIO_SID and TWILIO_AUTH:
        try:
            client = Client(TWILIO_SID, TWILIO_AUTH)
            # Add your phone verification logic here if needed for real users
            pass 
        except Exception as e:
            return jsonify({"error": "Twilio Error"}), 400

    return jsonify({"error": "Invalid Code"}), 401

@app.route('/api/specials')
def get_specials():
    # 2:30 AM Logic
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        current_day = (now - timedelta(days=1)).strftime('%A')
    else:
        current_day = now.strftime('%A')
    
    day = request.args.get('day', current_day)
    bars = Bar.query.filter_by(day=day).all()
    return jsonify([{ 'name': b.name, 'address': b.address, 'lat': b.lat, 'lng': b.lng, 'special': b.special } for b in bars])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
