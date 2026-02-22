from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "specials.json")

os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)


def load_specials():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(DATA_FILE, "w") as f:
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
