from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
# This secret key is what keeps you logged in
app.secret_key = os.environ.get('SECRET_KEY', 'beer_dollars_master_1616')

# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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
    if session.get('authorized'):
        return redirect(url_for('main_app'))
    return render_template('splash.html')

@app.route('/main')
def main_app():
    if not session.get('authorized'):
        return redirect(url_for('splash'))
    return render_template('index.html')

@app.route('/api/verify-code', methods=['POST'])
def verify():
    data = request.json
    code = data.get('code')
    
    # MASTER OVERRIDE
    if code in ["1616", "0000", "9999"]:
        session.permanent = True
        session['authorized'] = True
        return jsonify({"status": "success"})
    
    return jsonify({"error": "Invalid Code"}), 401

@app.route('/api/specials')
def get_specials():
    now = datetime.now()
    # 2:30 AM Bar Time Logic
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        default_day = (now - timedelta(days=1)).strftime('%A')
    else:
        default_day = now.strftime('%A')
    
    day = request.args.get('day', default_day)
    bars = Bar.query.filter_by(day=day).all()
    return jsonify([{
        'name': b.name, 'address': b.address, 
        'lat': b.lat, 'lng': b.lng, 'special': b.special
    } for b in bars])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
