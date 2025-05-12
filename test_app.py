import os
import json
import pytest
from unittest.mock import patch
from app import app, DATA_FILE


def test_app_is_up():
    assert app is not None

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def cleanup_data_file():
    # Clean up telemetry_log.json before and after tests
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    yield
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

def test_dashboard_empty(client):
    """Test dashboard with no telemetry"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Router Telemetry Dashboard' in response.data
    assert b'<td>' not in response.data  # No rows yet

@patch('app.send_slack_notification')
def test_mqtt_post_and_dashboard(mock_slack, client):
    """Test posting telemetry and dashboard update"""
    telemetry = {
        "uptime": "5 days",
        "cpu_temp": "55900",
        "wan_ip": "4.5.5.1"
    }

    # Post telemetry
    response = client.post('/mqtt', json=telemetry)
    assert response.status_code == 200
    assert response.get_json() == {"status": "published"}

    # Slack notification should have been called once
    assert mock_slack.called
    args, kwargs = mock_slack.call_args
    assert 'uptime' in args[0]
    assert args[0]['uptime'] == telemetry['uptime']

    # Dashboard should show data
    response = client.get('/')
    assert response.status_code == 200
    assert b'5 days' in response.data
    assert b'55900' in response.data
    assert b'4.5.5.1' in response.data
