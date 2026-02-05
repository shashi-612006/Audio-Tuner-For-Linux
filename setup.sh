
#!/bin/bash


set -e

BAR="============================================================"

echo "$BAR"
echo "   AirTIGHT: CROSS-DISTRO INSTALLER"
echo "$BAR"

if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root (sudo ./setup.sh)"
  exit 1
fi


INSTALL_DIR="/opt/airtight"
BIN_LINK="/usr/local/bin/airtight"

echo "[*] Installing AirTIGHT to $INSTALL_DIR ..."
mkdir -p $INSTALL_DIR


cp -r src $INSTALL_DIR/
cp README.md $INSTALL_DIR/ 2>/dev/null || true


echo "[*] Detecting Package Manager..."
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
    echo "[!] No supported package manager found."
    exit 1
fi

echo "[*] Installing dependencies: $DEPS"
$PM $DEPS

echo "[*] Creating launcher..."
cat <<EOF > $BIN_LINK
#!/bin/bash
sudo python3 -m src.main --working-dir $INSTALL_DIR
EOF

chmod +x $BIN_LINK

# 5. Init System Detection
INIT=$(ps -p 1 -o comm=)
echo "[*] Detected Init System: $INIT"

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
    ;;
    
  *)
    echo "[!] Unknown init system. Skipping service setup."
    ;;
esac

echo "$BAR"
echo "   INSTALLATION COMPLETE"
echo "   Run 'airtight' to start the audit"
echo "$BAR"
