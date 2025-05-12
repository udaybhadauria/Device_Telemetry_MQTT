#!/bin/sh

# Get CPU temperature (if available)
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
  CPU_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
else
  CPU_TEMP="N/A"
fi

# Get system uptime (human-readable)
UPTIME=$(uptime | sed 's/.*up \([^,]*\),.*/\1/' | xargs)

# Get public WAN IP (fallback if curl fails)
WAN_IP=$(curl -s ifconfig.me || echo "Unavailable")

# Replace <RPI_IP> with the actual IP address of your Raspberry Pi
curl -X POST http://<RPI-IP>:9090/mqtt \
  -H "Content-Type: application/json" \
  -d "{\"uptime\": \"$UPTIME\", \"cpu_temp\": \"$CPU_TEMP\", \"wan_ip\": \"$WAN_IP\"}"
