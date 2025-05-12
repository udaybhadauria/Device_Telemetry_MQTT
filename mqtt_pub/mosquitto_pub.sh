#!/bin/sh

CPU_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
UPTIME=$(uptime | sed 's/.*up \([^,]*\),.*/\1/' | xargs)
WAN_IP=$(curl -s ifconfig.me)

mosquitto_pub -h <RPI_IP> -t router/telemetry -m "{\"cpu_temp\": \"$CPU_TEMP\", \"uptime\": \"$UPTIME\", \"wan_ip\": \"$WAN_IP\"}"
