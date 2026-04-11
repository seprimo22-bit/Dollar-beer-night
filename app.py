import os
import json
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Render's DATABASE_URL fix
uri = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

@app.route('/get_json_bars')
def get_json_bars():
    try:
        with open('specials.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_db_bars')
def get_db_bars():
    day = request.args.get('day')
    bars = Bar.query.filter_by(day=day).all()
    return jsonify([{"name": b.name, "address": b.address, "special": b.special, "lat": b.lat, "lng": b.lng} for b in bars])

@app.route('/add_bar', methods=['POST'])
def add_bar():
    data = request.json
    new_bar = Bar(
        name=data['name'],
        address=data['address'],
        special=data['special'],
        day=data['day'],
        lat=data['lat'],
        lng=data['lng']
    )
    db.session.add(new_bar)
    db.session.commit()
    return jsonify({"success": True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
