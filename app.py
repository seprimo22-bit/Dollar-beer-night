from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database Configuration (Linking to your Render/SQL setup)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///beer_dollars.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for Bars/Specials
class Bar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    special = db.Column(db.String(250))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bars')
def get_bars():
    # Pulls all bars currently in your database
    bars = Bar.query.all()
    return jsonify([{
        'name': b.name,
        'lat': b.lat,
        'lng': b.lng,
        'special': b.special
    } for b in bars])

if __name__ == '__main__':
    # Initialize DB tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    
