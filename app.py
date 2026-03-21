from flask import Flask, render_template, request, redirect, url_for
import os
import json

app = Flask(__name__)

# ------------------------------
# CONFIG
# ------------------------------
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "supersecretkey")
SPECIALS_FILE = 'specials.json'

# ------------------------------
# DATA FUNCTIONS
# ------------------------------
def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []
    with open(SPECIALS_FILE, 'r') as f:
        return json.load(f)

def save_special(name, address, price):
    specials = load_specials()
    specials.append({'name': name, 'address': address, 'price': price})
    with open(SPECIALS_FILE, 'w') as f:
        json.dump(specials, f, indent=4)

# ------------------------------
# ROUTES
# ------------------------------

# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')

# MAP PAGE
@app.route('/map')
def map_page():
    specials = load_specials()
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    return render_template('map.html', specials=specials, api_key=api_key)

# ADMIN PAGE
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        price = request.form.get('price')
        save_special(name, address, price)
        return redirect('/admin')
    specials = load_specials()
    return render_template('admin.html', specials=specials)

# TEST ROUTE
@app.route('/test')
def test():
    return "APP IS WORKING"

# ------------------------------
# RUN
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
