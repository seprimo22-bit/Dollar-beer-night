from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Change in production

# File to store bars
BARS_FILE = 'bars.json'

# Master override codes
MASTER_CODES = ['999-000', '1616']

# Load bars from file
def load_bars():
    if not os.path.exists(BARS_FILE):
        return []
    with open(BARS_FILE, 'r') as f:
        return json.load(f)

# Save bars to file
def save_bars(bars):
    with open(BARS_FILE, 'w') as f:
        json.dump(bars, f, indent=2)

# Determine current day considering 2:30 AM cutoff
def get_current_day():
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        # before 2:30 AM counts as previous day
        now -= timedelta(days=1)
    return now.strftime('%A')  # e.g., 'Thursday'

@app.route('/', methods=['GET', 'POST'])
def splash():
    if request.method == 'POST':
        phone = request.form.get('phone')
        code = request.form.get('code')
        if code in MASTER_CODES:
            session['authorized'] = True
            return redirect(url_for('main'))
        # Here you could implement SMS code verification logic
        if phone and code:
            # For MVP, assume any code works for now
            session['authorized'] = True
            return redirect(url_for('main'))
        return render_template('splash.html', error="Invalid code or phone.")
    return render_template('splash.html')

@app.route('/main')
def main():
    if not session.get('authorized'):
        return redirect(url_for('splash'))
    bars = load_bars()
    current_day = get_current_day()
    return render_template('index.html', bars=bars, current_day=current_day)

@app.route('/add_bar', methods=['POST'])
def add_bar():
    if not session.get('authorized'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    bars = load_bars()
    new_bar = {
        'name': data.get('name'),
        'address': data.get('address'),
        'special': data.get('special'),
        'day': data.get('day'),
        'verified': False,
        'lat': data.get('lat', 0),  # optional for map
        'lng': data.get('lng', 0)
    }
    bars.append(new_bar)
    save_bars(bars)
    return jsonify({'success': True, 'bar': new_bar})

if __name__ == '__main__':
    app.run(debug=True)
