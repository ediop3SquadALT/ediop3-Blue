sudo apt update
sudo apt install -y python3 python3-pip bluetooth bluez bluez-tools rfkill git
pip3 install pydbus
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
rfkill unblock bluetooth
bluetoothctl <<EOF
power on
agent on
default-agent
EOF
