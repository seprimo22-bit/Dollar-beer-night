import os
import json
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database configuration for your PostgreSQL on Render
app.config['SQLALCHEMY_DATABASE_SET_URL'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    special = db.Column(db.String(100))
    day = db.Column(db.String(20))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

@app.route('/')
def index():
    return render_template('index.html')

# This is the "Bridge" that pulls from your root specials.json
@app.route('/get_json_bars')
def get_json_bars():
    try:
        with open('specials.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This route pulls any bars users added to the database
@app.route('/get_db_bars')
def get_db_bars():
    day = request.args.get('day')
    bars = Bar.query.filter_by(day=day).all()
    return jsonify([{"name": b.name, "address": b.address, "special": b.special, "lat": b.lat, "lng": b.lng} for b in bars])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
