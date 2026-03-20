# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# ------------------------------
# 1️⃣ Create Flask app
# ------------------------------
app = Flask(__name__)

# Load config from environment variables or default
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
# 3️⃣ Define your database models
# ------------------------------
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Address {self.name}>"

# ------------------------------
# 4️⃣ Create tables safely
# ------------------------------
with app.app_context():
    db.create_all()

# ------------------------------
# 5️⃣ Define routes
# ------------------------------
@app.route("/")
def index():
    addresses = Address.query.all()
    return render_template("index.html", addresses=addresses)

@app.route("/add", methods=["POST"])
def add_address():
    name = request.form.get("name")
    street = request.form.get("street")
    city = request.form.get("city")
    state = request.form.get("state")
    zip_code = request.form.get("zip_code")

    if name and street and city and state and zip_code:
        new_address = Address(
            name=name,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code
        )
        db.session.add(new_address)
        db.session.commit()

    return redirect(url_for("index"))

# ------------------------------
# 6️⃣ Run server locally
# ------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
