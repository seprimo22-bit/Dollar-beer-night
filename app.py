from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# -------------------------
# Home Page
# -------------------------
@app.route("/")
def home():
    return """
    <h1>Dollar Beer Night App</h1>
    <p>App is running.</p>
    <p><a href='/event'>View Event</a></p>
    """


# -------------------------
# Event Info Page
# -------------------------
@app.route("/event")
def event():
    return """
    <h2>Dollar Beer Night</h2>
    <p>Check local listings for participating venues.</p>
    <p>Drink responsibly.</p>
    """


# -------------------------
# Simple Feedback Endpoint
# -------------------------
@app.route("/feedback", methods=["POST"])
def feedback():
    message = request.form.get("message")

    return jsonify({
        "status": "received",
        "message": message
    })


# -------------------------
# Run Server
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
