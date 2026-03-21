
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
    # ... rest of your model columns (Street, City, etc.)
