from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# ----------------------
# DATABASE CONFIG
# ----------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///beer.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ----------------------
# DATABASE MODEL
# ----------------------
class Special(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bar_name = db.Column(db.String(120), nullable=False)
    deal = db.Column(db.String(200), nullable=False)
    day = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ----------------------
# SEED VERIFIED REAL BARS
# (Runs only if DB empty)
# ----------------------
def seed_data():
    if Special.query.count() > 0:
        return

    seed = [
        Special(
            bar_name="Lanai Lounge — Boardman, Ohio",
            deal="$1.50 cans",
            day="Sunday",
            verified=True
        ),
        Special(
            bar_name="Steel City Bar & Grill — Youngstown",
            deal="$2 bottles (2–8 PM)",
            day="Saturday",
            verified=True
        ),
        Special(
            bar_name="John & Helen’s Tavern — Kensington",
            deal="$2.50 bottles",
            day="Wednesday",
            verified=True
        ),
        Special(
            bar_name="Quench Bar & Grill — Boardman",
            deal="$2.50 Tito shots",
            day="Tuesday",
            verified=True
        ),
        Special(
            bar_name="La Villa Tavern — Struthers",
            deal="$2 bottles",
            day="Monday",
            verified=True
        )
    ]

    db.session.add_all(seed)
    db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


# ----------------------
# ROUTES
# ----------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add_special", methods=["POST"])
def add_special():
    data = request.json

    special = Special(
        bar_name=data["bar_name"],
        deal=data["deal"],
        day=data["day"].capitalize(),
        verified=False  # user submissions start unverified
    )

    db.session.add(special)
    db.session.commit()

    return jsonify({"status": "Saved — Pending Verification"})


@app.route("/get_specials/<day>")
def get_specials(day):
    day = day.capitalize()

    specials = Special.query.filter_by(day=day).all()

    return jsonify([
        {
            "bar_name": s.bar_name,
            "deal": s.deal,
            "verified": s.verified
        }
        for s in specials
    ])


if __name__ == "__main__":
    app.run(debug=True)
