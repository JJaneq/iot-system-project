from flask import Flask, jsonify
from flask_cors import CORS
import db_manager
import os
import json
from dotenv import load_dotenv
load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db = db_manager.DBManager(db_name, db_user, db_password)

app = Flask(__name__)
CORS(app)

@app.get("/api/lastdata")
def get_last():
    return jsonify(db.get_last_sensors_data())

def run_api():
    app.run(host="0.0.0.0", port=3000)