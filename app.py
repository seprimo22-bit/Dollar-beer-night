from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = "specials.json"


# ---------- UTILITIES ----------

def load_specials():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def is_duplicate(existing, new):
    for item in existing:
        if (
            item["bar"].lower() == new["bar"].lower()
            and item["deal"].lower() == new["deal"].lower()
            and item["location"].lower() == new["location"].lower()
        ):
            return True
    return False


# ---------- API ROUTES ----------

@app.route("/api/specials", methods=["GET"])
def get_specials():
    return jsonify(load_specials())


@app.route("/api/add-special", methods=["POST"])
def add_special():
    data = request.json

    required = ["bar", "deal", "location"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing fields"}), 400

    specials = load_specials()

    new_entry = {
        "bar": data["bar"],
        "deal": data["deal"],
        "location": data["location"],
        "verified": False
    }

    if is_duplicate(specials, new_entry):
        return jsonify({"error": "Duplicate entry"}), 409

    specials.append(new_entry)
    save_specials(specials)

    return jsonify({"message": "Saved successfully"}), 201


# ---------- RUN ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
