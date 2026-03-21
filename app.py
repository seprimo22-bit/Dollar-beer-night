from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# ------------------------------
# 1️⃣ Create Flask app
# ------------------------------
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "supersecretkey")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", "sqlite:///beer_dollars.db"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ------------------------------
# 2️⃣ Initialize database
# ------------------------------
db = SQLAlchemy(app)

# ------------------------------
# 3️⃣ Database Model
# ------------------------------
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    street = db.Column(db.String(200))
    city = db.Column(db.String(100))

# ------------------------------
# 4️⃣ ROUTES (THIS IS WHAT YOU WERE MISSING)
# ------------------------------

# ✅ Homepage
@app.route('/')
def home():
    return redirect(url_for('map_page'))

# ✅ Map page
@app.route('/map')
def map_page():
    addresses = Address.query.all()
    return render_template('map.html', addresses=addresses)

# ✅ Admin page
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form.get('name')
        street = request.form.get('street')
        city = request.form.get('city')

        new_address = Address(name=name, street=street, city=city)
        db.session.add(new_address)
        db.session.commit()

        return redirect(url_for('admin'))

    addresses = Address.query.all()
    return render_template('admin.html', addresses=addresses)

# ------------------------------
# 5️⃣ Run app
# ------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
