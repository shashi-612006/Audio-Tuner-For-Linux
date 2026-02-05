#!/bin/bash

# AirTIGHT Bandwidth Sink
# Stresses WiFi to test Bluetooth audio stability

TARGET="8.8.8.8"
INTERFACE=$(ip route get $TARGET | awk '{print $5; exit}')
BAR="============================================================"

echo "$BAR"
echo "   AirTIGHT BANDWIDTH STRESS TEST"
echo "$BAR"
echo "[*] Using interface: $INTERFACE"
echo "[*] Press Ctrl+C to stop the test"
echo

# Background download loops (simulate heavy traffic)
download_stress() {
    while true; do
        curl -L https://speed.hetzner.de/100MB.bin -o /dev/null &
        curl -L https://speed.hetzner.de/100MB.bin -o /dev/null &
        wait
    done
}

# Mild ICMP load to keep RF active
ping_stress() {
    ping -i 0.2 $TARGET > /dev/null
}

trap "echo; echo '[*] Stopping stress test...'; kill 0" SIGINT

download_stress &
ping_stress
