from flask import Flask, render_template, request, redirect, url_for
import os
import json

app = Flask(__name__)

# ------------------------------
# CONFIG
# ------------------------------
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "supersecretkey")
STATIC_FOLDER = 'static'

# ------------------------------
# PATH TO DATA (for map pins / specials)
# ------------------------------
SPECIALS_FILE = 'specials.json'

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

# HOME
@app.route('/')
def home():
    return render_template('index.html')

# MAP
@app.route('/map')
def map_page():
    specials = load_specials()
    return render_template('map.html', specials=specials)

# ADMIN
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
