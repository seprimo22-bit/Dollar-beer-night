from flask import Flask, render_template, request, jsonify
import json, os

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
    return jsonify(load_specials())


@app.route("/api/specials", methods=["POST"])
def add_special():
    specials = load_specials()
    specials.append(request.json)
    save_specials(specials)
    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(debug=True)
