import time
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

WATCHED_FILE = "mqtt_broker.py"
SLACK_URL = os.getenv("SLACK_WEBHOOK_ROUTER_TELEMETRY")

def notify_slack(msg):
    if SLACK_URL:
        try:
            import requests
            requests.post(SLACK_URL, json={"text": msg})
        except Exception as e:
            print("Slack notify failed:", e)

def restart_broker():
    notify_slack("♻️ mqtt_broker.py changed. Restarting broker service...")
    subprocess.run(["sudo", "systemctl", "restart", "mqtt_broker.service"])

if __name__ == "__main__":
    notify_slack("🛡️ Watcher started")
    try:
        last_mtime = os.path.getmtime(WATCHED_FILE)
    except FileNotFoundError:
        last_mtime = None

    try:
        while True:
            try:
                current_mtime = os.path.getmtime(WATCHED_FILE)
                if last_mtime is None:
                    last_mtime = current_mtime

                if current_mtime != last_mtime:
                    print(f"Change detected in {WATCHED_FILE}")
                    restart_broker()
                    last_mtime = current_mtime
            except FileNotFoundError:
                print(f"{WATCHED_FILE} not found.")
            time.sleep(10)
    except KeyboardInterrupt:
        notify_slack("🛑 Watcher stopped")
