from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey123')

# Database connection helper
def get_db_connection():
    # This pulls the URL from your Render Environment Variables
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')
    return conn

# Master override codes
MASTER_CODES = ['999-000', '1616', '999']

def get_current_day():
    # Adjust for 2:30 AM cutoff
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        now -= timedelta(days=1)
    return now.strftime('%A') 

@app.route('/', methods=['GET', 'POST'])
def splash():
    if request.method == 'POST':
        code = request.form.get('code')
        if code in MASTER_CODES:
            session['authorized'] = True
            return redirect(url_for('main'))
    return render_template('splash.html')

@app.route('/main')
def main():
    if not session.get('authorized'):
        return redirect(url_for('splash'))
    
    current_day = get_current_day()
    
    # Fetch bars from PostgreSQL
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM bars WHERE day = %s OR day = 'Daily'", (current_day,))
    bars = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('index.html', bars=bars, current_day=current_day)

@app.route('/add_bar', methods=['POST'])
def add_bar():
    if not session.get('authorized'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Insert into PostgreSQL
    cur.execute("""
        INSERT INTO bars (name, address, special, day, lat, lng, verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        data.get('name'), 
        data.get('address'), 
        data.get('special'), 
        data.get('day'),
        data.get('lat', 0), 
        data.get('lng', 0),
        False # Default to unverified
    ))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
    
