from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__)

# -------------------------
# CONFIG
# -------------------------

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "specials.json")

# Ensure data folder exists
os.makedirs(DATA_DIR, exist_ok=True)


# -------------------------
# DATA UTILITIES
# -------------------------

def load_specials():
    """Load specials safely."""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_specials(data):
    """Save specials safely."""
    with open(DATA_FILE, "w") as f:
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

    if not data:
        return jsonify({"error": "No data provided"}), 400

    specials = load_specials()
    specials.append(data)
    save_specials(specials)

    return jsonify({"status": "added", "data": data})


@app.route("/api/specials/clear", methods=["POST"])
def clear_specials():
    save_specials([])
    return jsonify({"status": "cleared"})


# -------------------------
# ENTRY POINT
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
