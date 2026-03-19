from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Bar model
class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    deal = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)

db.create_all()

@app.route('/')
def index():
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    return render_template('index.html', google_maps_api_key=google_maps_api_key)

@app.route('/get_bars')
def get_bars():
    day = request.args.get('day')
    bars = Bar.query.filter_by(day=day).all()
    bars_data = [{
        'id': b.id,
        'name': b.name,
        'address': b.address,
        'deal': b.deal,
        'lat': b.lat,
        'lng': b.lng
    } for b in bars]
    return jsonify(bars_data)

@app.route('/add_bar', methods=['POST'])
def add_bar():
    data = request.json
    bar = Bar(
        name=data['name'],
        address=data.get('address', ''),
        deal=data['deal'],
        day=data['day'],
        lat=data.get('lat'),
        lng=data.get('lng')
    )
    db.session.add(bar)
    db.session.commit()
    return jsonify({'status': 'success', 'bar': data})

if __name__ == '__main__':
    app.run(debug=True)
