from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__)

# -----------------------------
# CONFIG
# -----------------------------

# If running on Render with disk mounted
if os.path.exists("/data"):
    DATA_FILE = "/data/specials.json"
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)
    DATA_FILE = os.path.join(DATA_DIR, "specials.json")

# Ensure file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# -----------------------------
# DATA FUNCTIONS
# -----------------------------

def load_specials():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_specials(specials):
    with open(DATA_FILE, "w") as f:
        json.dump(specials, f, indent=2)

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/specials", methods=["GET"])
def get_specials():
    specials = load_specials()
    return jsonify(specials)

@app.route("/api/specials", methods=["POST"])
def add_special():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    specials = load_specials()

    new_special = {
        "barName": data.get("barName", "").strip(),
        "deal": data.get("deal", "").strip(),
        "location": data.get("location", "").strip(),
        "day": data.get("day", "").strip()
    }

    # Prevent empty entries
    if not new_special["barName"] or not new_special["deal"]:
        return jsonify({"error": "Missing required fields"}), 400

    specials.append(new_special)
    save_specials(specials)

    return jsonify({"status": "added"}), 201

@app.route("/api/specials/clear", methods=["POST"])
def clear_specials():
    save_specials([])
    return jsonify({"status": "cleared"})

# -----------------------------
# ENTRY POINT
# -----------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
