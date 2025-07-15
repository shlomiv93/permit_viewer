from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/projects')
def get_projects():
    conn = sqlite3.connect('licensing_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    return jsonify(projects)
