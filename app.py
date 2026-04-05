from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# DATA REGISTRY (Update with your PostgreSQL database URL in Render)
bar_deals = [
    {"name": "Steel City", "day": "Saturday", "deal": "$2.50 Shots", "lat": 41.0998, "lng": -80.6495},
    {"name": "Quench", "day": "Saturday", "deal": "$3.00 Shots", "lat": 41.1005, "lng": -80.6550},
    {"name": "Casaloma", "day": "Saturday", "deal": "$2.00 Drafts", "lat": 41.0950, "lng": -80.6400}
]

def get_logical_day():
    # 2:30 AM LOGIC: If before 2:30 AM, it is still "last night" for bar specials
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        return (now - timedelta(days=1)).strftime('%A')
    return now.strftime('%A')

@app.route('/')
def index():
    return render_template('index.html', current_day=get_logical_day())

@app.route('/api/deals/<day>')
def get_deals(day):
    filtered = [d for d in bar_deals if d['day'].lower() == day.lower()]
    return jsonify(filtered)

if __name__ == '__main__':
    app.run(debug=True)
    
