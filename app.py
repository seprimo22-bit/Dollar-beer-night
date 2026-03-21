# app.py (place in root of repo, same level as templates and static folders)
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json

# Explicitly define template and static folder locations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')
static_dir = os.path.join(BASE_DIR, 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey')

SPECIALS_FILE = os.path.join(BASE_DIR, 'specials.json')

# ------------------------------
# Helper Functions
# ------------------------------
def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return {}
    with open(SPECIALS_FILE, 'r') as f:
        return json.load(f)

def save_specials(data):
    with open(SPECIALS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ------------------------------
# Splash / Phone Verification
# ------------------------------
@app.route('/', methods=['GET', 'POST'])
def splash():
    if request.method == 'POST':
        phone = request.form.get('phone')
        code = request.form.get('code')
        # Admin override
        if code == '0000':
            return redirect(url_for('index'))
        # Stubbed Twilio verification: accept any code for now
        return redirect(url_for('index'))
    return render_template('splash.html')

# ------------------------------
# Main App
# ------------------------------
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/get_specials')
def get_specials():
    day = request.args.get('day')
    specials = load_specials()
    return jsonify(specials.get(day, []))

# ------------------------------
# Admin Panel
# ------------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    specials = load_specials()
    if request.method == 'POST':
        day = request.form.get('day')
        name = request.form.get('name')
        deal = request.form.get('deal')
        address = request.form.get('address')
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        entry = {'name': name, 'deal': deal, 'address': address, 'lat': lat, 'lng': lng}
        specials.setdefault(day, []).append(entry)
        save_specials(specials)
        return redirect('/admin')
    return render_template('admin.html', specials=specials)

# ------------------------------
# Run
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
