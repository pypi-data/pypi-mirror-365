#!/usr/bin/env python3
"""
Enhanced demo file to show how the security scanner adds detailed comments with fixes.
This file contains intentional vulnerabilities for demonstration.
"""

import sqlite3
import subprocess
import hashlib
import pickle
from flask import Flask, request, render_template_string
import os

app = Flask(__name__)

# This will get a detailed security comment with fix above it
DATABASE_PASSWORD = "admin123"

# This will get a detailed security comment with fix above it
API_KEY = "sk-1234567890abcdef"

def get_user_by_id(user_id):
    """Function with SQL injection vulnerability."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # This will get a detailed security comment with fix above it
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

def ping_host(host):
    """Function with command injection vulnerability."""
    # This will get a detailed security comment with fix above it
    result = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return result

def read_file(filename):
    """Function with path traversal vulnerability."""
    # This will get a detailed security comment with fix above it
    with open(filename, 'r') as f:
        return f.read()

@app.route('/search')
def search():
    """Route with XSS vulnerability."""
    query = request.args.get('q', '')
    # This will get a detailed security comment with fix above it
    template = f"""
    <html>
        <body>
            <h1>Search Results for: {query}</h1>
            <p>No results found.</p>
        </body>
    </html>
    """
    return render_template_string(template)

def load_user_data(data):
    """Function with insecure deserialization vulnerability."""
    # This will get a detailed security comment with fix above it
    return pickle.loads(data)

def hash_password(password):
    """Function with weak crypto vulnerability."""
    # This will get a detailed security comment with fix above it
    return hashlib.md5(password.encode()).hexdigest()

# This will get a detailed security comment with fix above it
app.debug = True

def generate_token():
    """Function with insecure random vulnerability."""
    import random
    # This will get a detailed security comment with fix above it
    return random.randint(1000, 9999)

@app.route('/error')
def error_handler():
    """Route with information disclosure vulnerability."""
    error = request.args.get('error', '')
    # This will get a detailed security comment with fix above it
    return f"Error occurred: {error}", 500

if __name__ == '__main__':
    # This will get a detailed security comment with fix above it
    app.run(host='0.0.0.0', port=5000) 