from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import paho.mqtt.publish as mqtt_publish
import jwt
from functools import wraps
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("JWT_SECRET", "supersecretkey123")

# Load credentials from .env
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin") #Fallback username
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123") #Fallback password

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD must be set in environment variables.")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_ROUTER_TELEMETRY")

DATA_FILE = "telemetry_log.json"

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
  <h2>Router Telemetry Dashboard</h2>
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

# JWT token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            decoded_token = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )
        except ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except InvalidTokenError as e:
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401

        return f(*args, **kwargs)
    return decorated

# Login route
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Token expires in 1 hour (change 5 to 1 if desired)
        expiry_time = datetime.utcnow() + timedelta(hours=1)

        # Ensure 'exp' is stored as a timestamp (int)
        token = jwt.encode({
            'user': username,
            'exp': int(expiry_time.timestamp())  # << important fix
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            'token': token,
            'expires_in': expiry_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/mqtt', methods=['POST'])
@token_required
def mqtt_bridge():
    data = request.json
    data["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    logs = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            logs = json.load(f)

    logs.append(data)
    with open(DATA_FILE, 'w') as f:
        json.dump(logs, f, indent=2)

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

@app.route('/api/latest-result', methods=['GET'])
@token_required
def latest_result():
    if not os.path.exists(DATA_FILE):
        return jsonify({"error": "No telemetry data found"}), 404

    with open(DATA_FILE, 'r') as f:
        try:
            logs = json.load(f)
            if not logs:
                return jsonify({"error": "No telemetry data found"}), 404
            return jsonify(logs[-1])
        except json.JSONDecodeError:
            return jsonify({"error": "Corrupted telemetry file"}), 500

@app.route('/api/results', methods=['GET'])
@token_required
def all_results():
    if not os.path.exists(DATA_FILE):
        return jsonify([])

    with open(DATA_FILE, 'r') as f:
        try:
            logs = json.load(f)
            return jsonify(logs)
        except json.JSONDecodeError:
            return jsonify([]), 500


def send_slack_notification(data):
    msg = (
        f"📡 Telemetry received:\n"
        f"🕒 Timestamp: {data['timestamp']}\n"
        f"⏱ Uptime: {data.get('uptime', 'N/A')}\n"
        f"🌡 CPU Temp: {data.get('cpu_temp', 'N/A')}\n"
        f"🌐 WAN IP: {data.get('wan_ip', 'N/A')}"
    )
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json={"text": msg})
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, ssl_context=('cert.pem', 'key.pem'), debug=False)
