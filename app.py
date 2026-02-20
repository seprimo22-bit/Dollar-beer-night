from flask import Flask, render_template, request, jsonify
import json, os

app = Flask(__name__)
SPECIALS_FILE = "Specials.json"


# Load specials
def load_specials():
    if not os.path.exists(SPECIALS_FILE):
        return []
    with open(SPECIALS_FILE, "r") as f:
        return json.load(f)


# Save specials
def save_specials(data):
    with open(SPECIALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# Homepage
@app.route("/")
def home():
    return render_template("index.html")


# API: Get specials for map
@app.route("/api/specials", methods=["POST"])
def get_specials():
    specials = load_specials()
    return jsonify(specials)


# API: Add special (crowdsourced)
@app.route("/api/add_special", methods=["POST"])
def add_special():
    data = request.json
    specials = load_specials()

    specials.append({
        "name": data.get("name"),
        "deal": data.get("deal"),
        "address": data.get("address"),
        "lat": data.get("lat"),
        "lon": data.get("lon"),
        "days": data.get("days")
    })

    save_specials(specials)
    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(debug=True)
