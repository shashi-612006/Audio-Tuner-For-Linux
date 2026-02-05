#!/bin/bash

set -e

BAR="============================================================"
INSTALL_DIR="/opt/airtight"
BIN_LINK="/usr/local/bin/airtight"

echo "$BAR"
echo "   AirTIGHT: CROSS-DISTRO INSTALLER"
echo "$BAR"


if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root (sudo bash setup.sh)"
  exit 1
fi

echo "[*] Installing AirTIGHT to $INSTALL_DIR ..."
mkdir -p $INSTALL_DIR
cp -r src $INSTALL_DIR/
cp README.md $INSTALL_DIR/ 2>/dev/null || true

echo "[*] Detecting package manager..."

if command -v pacman &> /dev/null; then
    PM="pacman -S --needed --noconfirm"
    DEPS="python-psutil pciutils alsa-utils pipewire wireplumber"
elif command -v apt-get &> /dev/null; then
    PM="apt-get install -y"
    DEPS="python3-psutil pciutils alsa-utils pipewire wireplumber"
elif command -v dnf &> /dev/null; then
    PM="dnf install -y"
    DEPS="python3-psutil pciutils alsa-utils pipewire wireplumber"
else
    echo "[!] Unsupported package manager. Install dependencies manually."
    exit 1
fi

echo "[*] Installing dependencies: $DEPS"
$PM $DEPS


echo "[*] Creating 'airtight' command..."
cat <<EOF > $BIN_LINK
#!/bin/bash
sudo python3 -m src.main
EOF

chmod +x $BIN_LINK

# 5️⃣ Detect Init System
INIT=$(ps -p 1 -o comm=)
echo "[*] Detected init system: $INIT"

case $INIT in
  systemd)
    SERVICE_PATH="/etc/systemd/system/airtight.service"
    echo "[*] Creating systemd service..."
    cat <<EOF > $SERVICE_PATH
[Unit]
Description=AirTIGHT Audio Optimizer
After=network.target sound.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -m src.main
WorkingDirectory=$INSTALL_DIR
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    echo "[*] To enable auto-start: sudo systemctl enable --now airtight"
    ;;
    
  runit)
    SERVICE_PATH="/etc/sv/airtight"
    mkdir -p $SERVICE_PATH
    echo "[*] Creating runit service..."
    cat <<EOF > $SERVICE_PATH/run
#!/bin/sh
exec python3 $INSTALL_DIR/src/main.py
EOF
    chmod +x $SERVICE_PATH/run
    echo "[*] Enable with: ln -s /etc/sv/airtight /var/service/"
    ;;
    
  openrc)
    SERVICE_PATH="/etc/init.d/airtight"
    echo "[*] Creating OpenRC service..."
    cat <<EOF > $SERVICE_PATH
#!/sbin/openrc-run
command="/usr/bin/python3"
command_args="$INSTALL_DIR/src/main.py"
EOF
    chmod +x $SERVICE_PATH
    echo "[*] Enable with: rc-update add airtight default"
    ;;
    
  *)
    echo "[!] Unknown init system. Skipping service setup."
    ;;
esac

echo "$BAR"
echo "   INSTALLATION COMPLETE"
echo "   Run 'airtight' to start the audit"
echo "$BAR"
