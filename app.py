from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__, static_folder="static", template_folder="templates")

# -------------------------
# DATA SETUP (Render safe)
# -------------------------
DATA_DIR = os.path.join(os.getcwd(), "data")
SPECIALS_FILE = os.path.join(DATA_DIR, "specials.json")

os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(SPECIALS_FILE):
    with open(SPECIALS_FILE, "w") as f:
        json.dump([], f)


# -------------------------
# HELPERS
# -------------------------
def load_specials():
    try:
        with open(SPECIALS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/specials", methods=["GET"])
def get_specials():
    return jsonify(load_specials())


@app.route("/api/specials", methods=["POST"])
def add_special():
    data = request.json

    bar = data.get("bar")
    deal = data.get("deal")
    location = data.get("location")
    day = data.get("day")

    specials = load_specials()

    # Duplicate prevention
    for s in specials:
        if (
            s["bar"] == bar
            and s["deal"] == deal
            and s["location"] == location
            and s["day"] == day
        ):
            return jsonify({"status": "duplicate"})

    specials.append({
        "bar": bar,
        "deal": deal,
        "location": location,
        "day": day
    })

    save_specials(specials)

    return jsonify({"status": "added"})


if __name__ == "__main__":
    app.run(debug=True)
