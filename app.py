from flask import Flask, render_template, request, jsonify
import os, json

app = Flask(__name__)

DATA_DIR = "data"
SPECIALS_FILE = os.path.join(DATA_DIR, "specials.json")


def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []
    with open(SPECIALS_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/specials", methods=["GET"])
def get_specials():
    day = request.args.get("day", "").lower()
    specials = load_specials()

    if day:
        specials = [s for s in specials if s.get("day", "").lower() == day]

    return jsonify(specials)


@app.route("/api/add-special", methods=["POST"])
def add_special():
    new_special = request.json
    specials = load_specials()

    # Duplicate prevention
    for s in specials:
        if (
            s["bar"].lower() == new_special["bar"].lower()
            and s["day"].lower() == new_special["day"].lower()
        ):
            return jsonify({"error": "Duplicate special"}), 400

    specials.append(new_special)
    save_specials(specials)

    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
