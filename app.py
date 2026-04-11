from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '1616_override')

# DATABASE CONNECTION
# Render gives you "postgres://", but Python needs "postgresql://"
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
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

# THE MISSING LINK: Adding bars to the DB
@app.route('/api/add-bar', methods=['POST'])
def add_bar():
    data = request.json
    try:
        new_bar = Bar(
            name=data['name'],
            address=data['address'],
            lat=data['lat'],
            lng=data['lng'],
            special=data['special'],
            day=data['day']
        )
        db.session.add(new_bar)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/specials')
def get_specials():
    day = request.args.get('day')
    bars = Bar.query.filter_by(day=day).all()
    return jsonify([{
        'name': b.name, 'address': b.address, 
        'lat': b.lat, 'lng': b.lng, 'special': b.special
    } for b in bars])

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
