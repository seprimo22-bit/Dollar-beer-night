from flask import Flask, render_template, request, jsonify
import json, os, datetime

app = Flask(__name__)

DATA_FILE = "specials.json"


# ---------- DATA HELPERS ----------

def load_specials():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_specials(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- ROUTES ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/specials", methods=["GET"])
def get_specials():
    specials = load_specials()

    today = datetime.datetime.now().strftime("%A")

    filtered = [s for s in specials if s.get("day") == today]

    return jsonify(filtered)


@app.route("/api/specials", methods=["POST"])
def add_special():
    specials = load_specials()
    new = request.json

    new["validated"] = False
    new["timestamp"] = datetime.datetime.now().isoformat()

    specials.append(new)
    save_specials(specials)

    return jsonify({"status": "saved"})


if __name__ == "__main__":
    app.run(debug=True)
