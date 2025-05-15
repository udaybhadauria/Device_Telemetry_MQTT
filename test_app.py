import os
import json
import pytest
from dotenv import load_dotenv
from unittest.mock import patch
from mqtt_broker import app, DATA_FILE

# Load environment variables from .env
load_dotenv()
TEST_USERNAME = os.getenv("MQTT_USER")
TEST_PASSWORD = os.getenv("MQTT_PASSWORD")

def test_app_is_up():
    assert app is not None

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def cleanup_data_file():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    yield
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def get_token(client):
    """Authenticate and get JWT token"""
    response = client.post('/login', json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    return response.get_json()["token"]

def test_login_success(client):
    """Test login endpoint"""
    response = client.post('/login', json={
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200
    assert "token" in response.get_json()

def test_dashboard_empty(client):
    """Test dashboard with no telemetry"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Router Telemetry Dashboard' in response.data
    assert b'<td>' not in response.data  # No data rows yet

@patch('mqtt_broker.send_slack_notification')
def test_mqtt_post_and_dashboard(mock_slack, client):
    """Test telemetry POST + dashboard update"""
    token = get_token(client)
    telemetry = {
        "uptime": "5 days",
        "cpu_temp": "55900",
        "wan_ip": "4.5.5.1"
    }
    headers = {"Authorization": f"Bearer {token}"}

    # POST telemetry with token
    response = client.post('/mqtt', json=telemetry, headers=headers)
    assert response.status_code == 200
    assert response.get_json() == {"status": "published"}

    # Slack should be called
    assert mock_slack.called
    args, kwargs = mock_slack.call_args
    assert 'uptime' in args[0]
    assert args[0]['uptime'] == telemetry['uptime']

    # Dashboard must show values
    response = client.get('/')
    assert response.status_code == 200
    assert b'5 days' in response.data
    assert b'55900' in response.data
    assert b'4.5.5.1' in response.data
