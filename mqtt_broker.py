from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime
import requests
from dotenv import load_dotenv
import paho.mqtt.publish as mqtt_publish  # MQTT added

# Load the .env file
load_dotenv()

app = Flask(__name__)
DATA_FILE = "telemetry_log.json"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_ROUTER_TELEMETRY")  # Read from .env

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Telemetry Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h2 { color: #333; }
    table { border-collapse: collapse; width: 100%; }
    th, td {
      border: 1px solid #ccc;
      padding: 8px 12px;
      text-align: left;
    }
    th { background-color: #f5f5f5; }
    tr:nth-child(even) { background-color: #f9f9f9; }
  </style>
</head>
<body>
  <h2>Device Telemetry Dashboard</h2>
  <table>
    <thead>
      <tr>
        <th>Timestamp</th>
        <th>Uptime</th>
        <th>CPU Temp</th>
        <th>WAN IP</th>
      </tr>
    </thead>
    <tbody>
      {% for entry in logs %}
      <tr>
        <td>{{ entry.timestamp }}</td>
        <td>{{ entry.uptime }}</td>
        <td>{{ entry.cpu_temp }}</td>
        <td>{{ entry.wan_ip }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""

def send_slack_notification(data):
    msg = (
        f"📡 Telemetry received:\n"
        f"🕒 Timestamp: {data['timestamp']}\n"
        f"⏱ Uptime: {data.get('uptime', 'N/A')}\n"
        f"🌡 CPU Temp: {data.get('cpu_temp', 'N/A')}\n"
        f"🌐 WAN IP: {data.get('wan_ip', 'N/A')}"
    )
    payload = {"text": msg}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code != 200:
            print("Slack error:", response.text)
    except Exception as e:
        print("Failed to send Slack message:", e)

def publish_mqtt(data):
    try:
        mqtt_publish.single(
            topic="router/telemetry",
            payload=json.dumps(data),
            hostname="localhost"
        )
    except Exception as e:
        print("MQTT publish error:", e)

@app.route('/mqtt', methods=['POST'])
def mqtt_bridge():
    data = request.json
    data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Load existing logs
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(data)

    with open(DATA_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

    # Send Slack & MQTT
    send_slack_notification(data)
    publish_mqtt(data)

    return {"status": "published"}, 200

@app.route('/')
def dashboard():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    return render_template_string(HTML_TEMPLATE, logs=logs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)
