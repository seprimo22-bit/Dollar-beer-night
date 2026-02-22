from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__)

# -------------------------
# CONFIG
# -------------------------
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "specials.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure JSON file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


# -------------------------
# DATA FUNCTIONS
# -------------------------
def load_specials():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_specials(specials):
    with open(DATA_FILE, "w") as f:
        json.dump(specials, f, indent=2)


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

    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["barName", "deal", "location"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    specials = load_specials()

    specials.append({
        "barName": data["barName"],
        "deal": data["deal"],
        "location": data["location"],
        "day": data.get("day", "")
    })

    save_specials(specials)

    return jsonify({"status": "added"})


@app.route("/api/specials/clear", methods=["POST"])
def clear_specials():
    save_specials([])
    return jsonify({"status": "cleared"})


# -------------------------
# ENTRY POINT
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
