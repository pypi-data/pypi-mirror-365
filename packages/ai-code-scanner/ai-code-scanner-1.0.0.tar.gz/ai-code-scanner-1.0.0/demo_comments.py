#!/usr/bin/env python3
"""
Demo file to show how the security scanner adds comments.
This file contains intentional vulnerabilities for demonstration.
"""

import sqlite3
from flask import Flask, request

app = Flask(__name__)

# This line will get a security comment added above it
DATABASE_PASSWORD = "admin123"

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # This line will get a security comment added above it
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # This line will get a security comment added above it
    return f"<h1>Search Results for: {query}</h1>"

if __name__ == '__main__':
    app.run(debug=True)  # This line will get a security comment added above it 