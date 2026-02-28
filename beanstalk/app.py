from flask import Flask, render_template, request, jsonify
from datetime import datetime
import mysql.connector
import os

app = Flask(__name__)

RDS_HOST = os.environ.get('RDS_HOST')
RDS_USER = os.environ.get('RDS_USER')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD')
DB_NAME = os.environ.get('DB_NAME')

def get_db_connection():
    return mysql.connector.connect(host = RDS_HOST, user = RDS_USER, password = RDS_PASSWORD, database = DB_NAME)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/visit', methods = ['GET'])
def visit():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM visits')
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({'visits' : count})

@app.route('/store_ip', methods = ['POST'])
def store_ip():
    ip = request.remote_addr
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO visits (ip) VALUES (%s)', (ip,))
    conn.commit()
    cursor.close()
    conn.close()
    return {'message' : 'IP Logged', 'ip' : ip}

@app.route('/ips', methods=['GET'])
def get_ips():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT ip FROM visits')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    ips = [row[0] for row in rows]
    return {'logged_ips' : ips}

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/monthly_stats', methods = ['GET'])
def monthly_stats():
    month = request.args.get('month', default = datetime.now().month, type = int)
    year = request.args.get('year', default = datetime.now().year, type = int)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM visits WHERE MONTH(visit_time) = %s AND YEAR(visit_time) = %s', (month, year))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {'year' : year, 'month' : month, 'visits' : count}

@app.route('/daily_stats', methods = ['GET'])
def daily_stats():
    month = request.args.get('month', default = datetime.now().month, type = int)
    year = request.args.get('year', default = datetime.now().year, type = int)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DAY(visit_time) as day, COUNT(*) as visits 
        FROM visits 
        WHERE MONTH(visit_time) = %s AND YEAR(visit_time) = %s 
        GROUP BY DAY(visit_time) 
        ORDER BY DAY(visit_time)
    ''', (month, year))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    daily_data = [{'day': row[0], 'visits': row[1]} for row in rows]
    return {'year': year, 'month': month, 'daily_stats': daily_data}

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get('PORT', 5000))
    app.run(host = '0.0.0.0', port = port, debug = False)