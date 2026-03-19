import os
import sqlite3
from flask import Flask, request

app = Flask(__name__)

@app.route('/scan')
def do_scan():
    # 1. Command Injection (CRITICAL)
    # Source: request.args -> Sink: os.system
    cmd = request.args.get('cmd')
    os.system(cmd) 

    # 2. SQL Injection (CRITICAL)
    # Source: request.args -> Sink: cursor.execute
    user_id = request.args.get('id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    
    return "Scan Complete"

# 3. Hardcoded Secret (HIGH)
# CodeQL scans for this pattern automatically
API_KEY = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

if __name__ == "__main__":
    app.run()
