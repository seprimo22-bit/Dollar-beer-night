from flask import Flask, request, jsonify, render_template
import json, os, math, datetime, requests

app = Flask(__name__)

DATA_FILE = "Specials.json"
LOCATIONIQ_KEY = "pk.294e06f9df72782c42392cee32c94dd9"


# ---------- Load / Save ----------

def load_specials():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_specials(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------- Distance ----------

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# ---------- Geocode ----------

def geocode_bar(query):
    url = "https://us1.locationiq.com/v1/search.php"

    params = {
        "key": LOCATIONIQ_KEY,
        "q": query + " Ohio USA",
        "format": "json"
    }

    try:
        r = requests.get(url, params=params, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        print("Geocode error:", e)

    return None, None


# ---------- Routes ----------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/add_special", methods=["POST"])
def add_special():

    data = request.json
    name = data.get("name","").strip()
    deal = data.get("deal","").strip()
    address = data.get("address","").strip()
    day = data.get("day","").strip().lower()

    if not name or not deal or not day:
        return jsonify({"error":"Missing info"}), 400

    # Try address first, fallback to name
    lat, lng = geocode_bar(address if address else name)

    if lat is None:
        return jsonify({"error":"Could not locate bar"}), 400

    specials = load_specials()

    specials.append({
        "name": name,
        "deal": deal,
        "address": address,
        "day": day,
        "lat": lat,
        "lng": lng,
        "verified": False,
        "timestamp": datetime.datetime.now().isoformat()
    })

    save_specials(specials)

    return jsonify({"status":"saved"})


@app.route("/api/specials")
def get_specials():

    specials = load_specials()

    user_lat = float(request.args.get("lat"))
    user_lng = float(request.args.get("lng"))
    today = datetime.datetime.now().strftime("%A").lower()

    results = []

    for s in specials:

        # Show today's specials only
        if s.get("day") != today:
            continue

        dist = haversine(user_lat, user_lng, s["lat"], s["lng"])
        s["distance"] = round(dist, 1)
        results.append(s)

    results.sort(key=lambda x: x["distance"])

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
