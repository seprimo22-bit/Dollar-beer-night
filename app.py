from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# ------------------------------
# HOME PAGE
# ------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# ------------------------------
# MAP PAGE
# ------------------------------
@app.route('/map')
def map_page():
    return render_template('map.html')

# ------------------------------
# ADMIN PAGE
# ------------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # just testing form submission for now
        name = request.form.get('name')
        print(f"Added: {name}")

        return redirect('/admin')

    return render_template('admin.html')

# ------------------------------
# TEST ROUTE (IMPORTANT)
# ------------------------------
@app.route('/test')
def test():
    return "APP IS WORKING"

# ------------------------------
# RUN
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
