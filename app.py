from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime, timedelta
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
# Secure the session
app.secret_key = os.environ.get('SECRET_KEY', 'beer_dollars_999_security')

# 1. Master Override Codes
MASTER_CODES = ['999', '1616', '999-000']

def get_db_connection():
    # Pulls the new database URL from your Render Environment Variables
    return psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')

def get_business_day():
    # The 2:30 AM Rule: If it's 1:00 AM Saturday, it's still Friday night.
    now = datetime.now()
    if now.hour < 2 or (now.hour == 2 and now.minute < 30):
        now -= timedelta(days=1)
    return now.strftime('%A') # Returns 'Friday', 'Saturday', etc.

@app.route('/', methods=['GET', 'POST'])
def splash():
    if request.method == 'POST':
        phone = request.form.get('phone')
        code = request.form.get('code')
        
        # MASTER OVERRIDE CHECK
        if code in MASTER_CODES:
            session['authorized'] = True
            return redirect(url_for('main'))
        
        # Twilio Placeholder (If you enter a phone and any code, it lets you in for now)
        if phone and code:
            session['authorized'] = True
            return redirect(url_for('main'))
            
    return render_template('splash.html')

@app.route('/main')
def main():
    # Gatekeeper: Redirect to splash if not logged in
    if not session.get('authorized'):
        return redirect(url_for('splash'))
    
    current_day = get_business_day()
    return render_template('index.html', current_day=current_day)

@app.route('/api/bars')
def get_bars():
    # This API handles the 50-mile radius and the day filtering
    day = request.args.get('day', get_business_day())
    user_lat = float(request.args.get('lat', 0))
    user_lng = float(request.args.get('lng', 0))
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Haversine formula to find bars within 50 miles
    query = """
        SELECT *, 
        (3959 * acos(cos(radians(%s)) * cos(radians(lat)) * cos(radians(lng) - radians(%s)) + sin(radians(%s)) * sin(radians(lat)))) AS distance 
        FROM bars 
        WHERE (day = %s OR day = 'Daily')
        GROUP BY id
        HAVING (3959 * acos(cos(radians(%s)) * cos(radians(lat)) * cos(radians(lng) - radians(%s)) + sin(radians(%s)) * sin(radians(lat)))) < 50
        ORDER BY distance ASC;
    """
    cur.execute(query, (user_lat, user_lng, user_lat, day, user_lat, user_lng, user_lat))
    bars = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(bars)

@app.route('/add_bar', methods=['POST'])
def add_bar():
    if not session.get('authorized'):
        return jsonify({'status': 'unauthorized'}), 401
        
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Insert new bar - Defaulted to NOT verified (Matthew's manual check)
    cur.execute("""
        INSERT INTO bars (name, address, special, day, lat, lng, verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (data['name'], data['address'], data['special'], data['day'], data['lat'], data['lng'], False))
    
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
    
