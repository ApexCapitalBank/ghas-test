import os
import sqlite3
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/vuln')
def trigger_alerts():
    # 1. Command Injection (Critical)
    cmd = request.args.get('cmd')
    os.system(cmd) 

    # 2. SQL Injection (Critical)
    user_id = request.args.get('id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

    # 3. Reflected XSS (High)
    name = request.args.get('name')
    return make_response(f"Hello {name}")

    # 4. Unsafe Eval (High)
    calc = request.args.get('calc')
    return eval(calc)

# 5. Hardcoded Secret (Detected automatically)
ADMIN_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

if __name__ == "__main__":
    app.run()
