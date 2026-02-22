from flask import Flask, request, jsonify, render_template
from flask import Flask, render_template, request, jsonify
import os
import json
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

DATA_DIR = "data"
SPECIALS_FILE = os.path.join(DATA_DIR, "specials.json")

os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
# Ensure file exists but DON'T overwrite
if not os.path.exists(SPECIALS_FILE):
    with open(SPECIALS_FILE, "w") as f:
        json.dump([], f)


def load_specials():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(DATA_FILE, "w") as f:
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


@app.route("/api/specials", methods=["GET", "POST"])
def specials():

    if request.method == "POST":
        new_special = request.json
        specials = load_specials()

        # Duplicate prevention
        for s in specials:
            if (
                s["bar"].lower() == new_special["bar"].lower()
                and s["day"].lower() == new_special["day"].lower()
            ):
                return jsonify({"status": "duplicate"}), 400

        specials.append(new_special)
        save_specials(specials)
        return jsonify({"status": "saved"})

    # GET
    day = request.args.get("day")
    specials = load_specials()

    if day:
        specials = [s for s in specials if s["day"].lower() == day.lower()]

    return jsonify(specials)
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
