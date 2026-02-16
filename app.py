from flask import Flask, render_template, request, jsonify
import json, os, datetime

app = Flask(__name__)
DATA_FILE = "specials.json"


def load_specials():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/specials", methods=["GET"])
def get_specials():
    day = request.args.get("day")
    specials = load_specials()

    if day:
        specials = [s for s in specials if s.get("day") == day]

    return jsonify(specials)


@app.route("/api/specials", methods=["POST"])
def add_special():
    specials = load_specials()
    new = request.json

    new["timestamp"] = datetime.datetime.now().isoformat()

    specials.append(new)
    save_specials(specials)

    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(debug=True)
