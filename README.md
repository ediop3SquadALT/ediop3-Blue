# ediop3-Blue
A bluetooth exploitation tool does hid trough bluetooth 
remember it won't work if target isn't vulnerable to CVE-2023-45866 or is patched.

steps to do
(only works on OS's like kali parrot os. and it ofc requires root)

sudo apt update && sudo apt install -y python3 python3-pip bluetooth bluez bluez-tools bluez-hcidump libbluetooth-dev libglib2.0-dev && pip3 install pygatt

there.

