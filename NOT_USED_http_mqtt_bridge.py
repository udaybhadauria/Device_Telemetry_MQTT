from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "telemetry_log.json"

@app.route('/mqtt', methods=['POST'])
def mqtt_bridge():
    data = request.json
    data["timestamp"] = datetime.now().isoformat()

    # Load existing data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            logs = json.load(f)
    else:
        logs = []

    # Append new entry
    logs.append(data)
    with open(DATA_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

    return {"status": "published"}, 200

@app.route('/', methods=['GET'])
def show_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            logs = json.load(f)
        return jsonify(logs)
    else:
        return jsonify({"message": "No data yet."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
