"""
Deliberately vulnerable Python application for generating GitHub Advanced Security / CodeQL findings.
DO NOT use in production. This is for testing SARIF export only.
"""

import os
import sys
import pickle
import subprocess
import sqlite3
import hashlib
import tempfile
import yaml
import xml.etree.ElementTree as ET
from flask import Flask, request, redirect, make_response, send_file, session, jsonify

app = Flask(__name__)

# CWE-798: Hardcoded credentials
DATABASE_PASSWORD = "SuperSecret123!"
API_KEY = "AKIAIOSFODNN7EXAMPLE"
SECRET_KEY = "sk_live_4eC39HqLyjWDarjtT1zdp7dc"
app.secret_key = "hardcoded-secret-key-do-not-use"

# CWE-327: Use of broken cryptographic algorithm
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def hash_password_sha1(password):
    return hashlib.sha1(password.encode()).hexdigest()


# CWE-89: SQL Injection (multiple variants)
def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

def search_users(search_term):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE name LIKE '%" + search_term + "%'")
    return cursor.fetchall()

def delete_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    conn.commit()

def update_user_email(user_id, email):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = '%s' WHERE id = %s" % (email, user_id))
    conn.commit()


# CWE-78: OS Command Injection (multiple variants)
@app.route("/ping")
def ping():
    host = request.args.get("host")
    result = os.system("ping -c 1 " + host)
    return str(result)

@app.route("/lookup")
def lookup():
    domain = request.args.get("domain")
    result = subprocess.check_output("nslookup " + domain, shell=True)
    return result

@app.route("/execute")
def execute():
    cmd = request.args.get("cmd")
    result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = result.communicate()
    return stdout

@app.route("/system_info")
def system_info():
    tool = request.args.get("tool", "uname")
    output = os.popen(tool + " -a").read()
    return output


# CWE-79: Cross-Site Scripting (Reflected XSS)
@app.route("/greet")
def greet():
    name = request.args.get("name", "World")
    return "<h1>Hello, " + name + "!</h1>"

@app.route("/search")
def search():
    query = request.args.get("q", "")
    return f"<html><body><h1>Search results for: {query}</h1></body></html>"

@app.route("/error")
def error_page():
    msg = request.args.get("msg", "Unknown error")
    return make_response("<div class='error'>" + msg + "</div>", 400)


# CWE-22: Path Traversal
@app.route("/download")
def download():
    filename = request.args.get("file")
    filepath = os.path.join("/var/www/files", filename)
    return send_file(filepath)

@app.route("/read")
def read_file():
    path = request.args.get("path")
    with open(path, "r") as f:
        return f.read()

@app.route("/logs")
def view_logs():
    log_name = request.args.get("name")
    log_path = "/var/log/" + log_name
    with open(log_path) as f:
        return f.read()


# CWE-502: Deserialization of Untrusted Data
@app.route("/load_object", methods=["POST"])
def load_object():
    data = request.get_data()
    obj = pickle.loads(data)
    return str(obj)

@app.route("/load_yaml", methods=["POST"])
def load_yaml_data():
    data = request.get_data()
    result = yaml.load(data, Loader=yaml.Loader)
    return str(result)


# CWE-611: XML External Entity (XXE) Injection
@app.route("/parse_xml", methods=["POST"])
def parse_xml():
    xml_data = request.get_data()
    tree = ET.fromstring(xml_data)
    return ET.tostring(tree).decode()


# CWE-601: Open Redirect
@app.route("/redirect")
def open_redirect():
    url = request.args.get("url")
    return redirect(url)

@app.route("/goto")
def goto():
    target = request.args.get("target")
    return redirect(target, code=302)


# CWE-312: Cleartext Storage of Sensitive Information
@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    ssn = request.form.get("ssn")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, ssn) VALUES ('"
        + username + "', '" + password + "', '" + ssn + "')"
    )
    conn.commit()

    with open("app.log", "a") as log:
        log.write(f"New user registered: {username}, password: {password}, SSN: {ssn}\n")

    return "Registered"


# CWE-330: Use of insufficiently random values
import random

@app.route("/generate_token")
def generate_token():
    token = random.randint(100000, 999999)
    return {"token": token}

@app.route("/reset_password")
def reset_password():
    reset_code = str(random.random())
    return {"reset_code": reset_code}


# CWE-918: Server-Side Request Forgery (SSRF)
import urllib.request

@app.route("/fetch")
def fetch_url():
    url = request.args.get("url")
    response = urllib.request.urlopen(url)
    return response.read()

@app.route("/proxy")
def proxy():
    target = request.args.get("target")
    import requests as req
    resp = req.get(target)
    return resp.text


# CWE-94: Code Injection
@app.route("/calculate")
def calculate():
    expression = request.args.get("expr")
    result = eval(expression)
    return str(result)

@app.route("/run_code", methods=["POST"])
def run_code():
    code = request.form.get("code")
    exec(code)
    return "Executed"

@app.route("/template")
def template():
    template_str = request.args.get("tpl")
    compiled = compile(template_str, "<string>", "exec")
    exec(compiled)
    return "Done"


# CWE-295: Improper Certificate Validation
import ssl
import requests

def fetch_insecure(url):
    return requests.get(url, verify=False)

def create_insecure_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


# CWE-117: Log Injection
import logging

logger = logging.getLogger(__name__)

@app.route("/log_action")
def log_action():
    user_input = request.args.get("action")
    logger.info("User performed action: " + user_input)
    return "Logged"


# CWE-209: Information Exposure Through Error Messages
@app.route("/debug")
def debug_endpoint():
    try:
        user_id = request.args.get("id")
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = " + user_id)
        return str(cursor.fetchone())
    except Exception as e:
        return f"<pre>Error: {str(e)}\nStack trace:\n{sys.exc_info()}</pre>", 500


# CWE-250: Execution with Unnecessary Privileges
@app.route("/admin/restart")
def restart_service():
    service = request.args.get("service")
    os.system("sudo systemctl restart " + service)
    return "Restarted"


# CWE-377: Insecure Temporary File
@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_data()
    tmp_path = "/tmp/upload_" + str(random.randint(1000, 9999))
    with open(tmp_path, "wb") as f:
        f.write(data)
    return {"path": tmp_path}


# CWE-732: Incorrect Permission Assignment
@app.route("/save_config", methods=["POST"])
def save_config():
    config_data = request.get_data()
    config_path = "/etc/myapp/config.json"
    with open(config_path, "wb") as f:
        f.write(config_data)
    os.chmod(config_path, 0o777)
    return "Saved"


# CWE-532: Information Exposure Through Log Files
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    credit_card = request.form.get("cc")

    logger.info(f"Login attempt: user={username}, pass={password}, cc={credit_card}")

    if username == "admin" and password == DATABASE_PASSWORD:
        session["user"] = username
        return "OK"
    return "Failed", 401


# CWE-319: Cleartext Transmission of Sensitive Information
@app.route("/api/send_credentials")
def send_creds():
    return jsonify({
        "db_host": "prod-db.internal.company.com",
        "db_user": "root",
        "db_pass": DATABASE_PASSWORD,
        "api_key": API_KEY,
    })


# CWE-400: Uncontrolled Resource Consumption (ReDoS)
import re

@app.route("/validate_email")
def validate_email():
    email = request.args.get("email")
    pattern = r"^([a-zA-Z0-9_\-\.]+)*@([a-zA-Z0-9_\-\.]+)*\.([a-zA-Z]{2,5})$"
    if re.match(pattern, email):
        return "Valid"
    return "Invalid"


# CWE-776: Improper Restriction of Recursive Entity References (Billion Laughs)
@app.route("/parse_document", methods=["POST"])
def parse_document():
    from lxml import etree
    xml_data = request.get_data()
    parser = etree.XMLParser(resolve_entities=True)
    doc = etree.fromstring(xml_data, parser)
    return etree.tostring(doc).decode()


# Multiple additional SQL injections
@app.route("/api/products")
def get_products():
    category = request.args.get("category")
    price = request.args.get("max_price")
    conn = sqlite3.connect("shop.db")
    c = conn.cursor()
    c.execute(f"SELECT * FROM products WHERE category = '{category}' AND price < {price}")
    return str(c.fetchall())

@app.route("/api/orders")
def get_orders():
    status = request.args.get("status")
    conn = sqlite3.connect("shop.db")
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE status = '" + status + "' ORDER BY date DESC")
    return str(c.fetchall())


if __name__ == "__main__":
    # CWE-489: Debug mode in production
    app.run(host="0.0.0.0", port=80, debug=True)
