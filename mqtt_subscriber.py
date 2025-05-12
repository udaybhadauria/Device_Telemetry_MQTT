import paho.mqtt.client as mqtt
import json
from datetime import datetime

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("router/telemetry")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"[{datetime.now()}] Received: {payload}")
    with open("/home/pi/telemetry_log.json", "a") as f:
        f.write(payload + '\n')

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
