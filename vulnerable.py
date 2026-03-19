# Create a file named 'vulnerable.py' with multiple security issues
content = """
import os
import sqlite3
import base64

# 1. Hardcoded password/secret
API_KEY = "sk-1234567890abcdef1234567890abcdef"

# 2. SQL Injection
def get_user_data(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Unsafe: Direct string formatting into a query
    query = "SELECT * FROM users WHERE id = '%s'" % user_id
    cursor.execute(query)
    return cursor.fetchone()

# 3. OS Command Injection
def ping_host(host):
    # Unsafe: User input directly in a system shell command
    os.system("ping -c 1 " + host)

# 4. Insecure Cryptography (Base64 is not encryption)
def store_secret(secret):
    encoded = base64.b64encode(secret.encode())
    print(f"Stored 'encrypted' secret: {encoded}")

# 5. Use of unsafe 'eval'
def calculate(expression):
    return eval(expression)
"""

with open("vulnerable.py", "w") as f:
    f.write(content.strip())

print("Successfully generated 'vulnerable.py' with 5 security flaws.")
