import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv() # This loads your .env file

app = Flask(__name__)

# This is where your API key lives
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")

@app.route('/')
def index():
    # We pass the key here so the HTML can use it
    return render_template('index.html', GOOGLE_MAPS_KEY=GOOGLE_MAPS_KEY)

@app.route('/api/specials', methods=['GET'])
def get_specials():
    # Logic to pull from your database
    return jsonify([]) 

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
