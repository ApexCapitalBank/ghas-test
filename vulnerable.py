import os
import sqlite3
import base64
from flask import Flask, request, make_response

app = Flask(__name__)

@app.route('/test')
def test_vulns():
    # 1. OS Command Injection (Critical)
    # Source: request.args -> Sink: os.system
    cmd = request.args.get('cmd')
    os.system(f"echo {cmd}")

    # 2. SQL Injection (Critical)
    # Source: request.args -> Sink: cursor.execute
    user_id = request.args.get('id')
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

    # 3. Reflected Cross-Site Scripting (XSS) (High)
    # Source: request.args -> Sink: make_response
    name = request.args.get('name')
    return make_response(f"<h1>Hello {name}</h1>")

@app.route('/danger')
def more_danger():
    # 4. Unsafe Deserialization (Critical)
    # Source: request.args -> Sink: eval
    data = request.args.get('data')
    result = eval(data)

    # 5. Path Traversal (High)
    # Source: request.args -> Sink: open
    filename = request.args.get('file')
    with open(f"/var/www/html/{filename}", "r") as f:
        return f.read()

# 6. Hardcoded Secret (Medium/High) - Scanned automatically
INTERNAL_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

if __name__ == "__main__":
    app.run()
