import paho.mqtt.publish as publish
import subprocess
import json

cpu_temp = subprocess.getoutput("cat /sys/class/thermal/thermal_zone0/temp")
uptime = subprocess.getoutput("uptime | sed 's/.*up \([^,]*\),.*/\1/' | xargs")
wan_ip = subprocess.getoutput("curl -s ifconfig.me")

data = {
    "cpu_temp": cpu_temp,
    "uptime": uptime,
    "wan_ip": wan_ip
}

publish.single("router/telemetry", payload=json.dumps(data), hostname="<RPI_IP>")
