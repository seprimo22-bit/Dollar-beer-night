from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__, static_folder="static", template_folder="templates")

DATA_DIR = "data"
SPECIALS_FILE = os.path.join(DATA_DIR, "specials.json")

os.makedirs(DATA_DIR, exist_ok=True)

# Ensure file exists but DON'T overwrite
if not os.path.exists(SPECIALS_FILE):
    with open(SPECIALS_FILE, "w") as f:
        json.dump([], f)


def load_specials():
    try:
        with open(SPECIALS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/specials")
def get_specials():
    day = request.args.get("day")
    specials = load_specials()

    if day:
        specials = [
            s for s in specials
            if s.get("day", "").lower() == day.lower()
        ]

    return jsonify(specials)


@app.route("/api/add-special", methods=["POST"])
def add_special():
    data = request.json
    specials = load_specials()

    # duplicate prevention
    for s in specials:
        if (
            s["bar"].lower() == data["bar"].lower()
            and s["day"].lower() == data["day"].lower()
        ):
            return jsonify({"error": "Already exists"}), 400

    specials.append(data)
    save_specials(specials)

    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
