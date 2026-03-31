import socket
import threading
import json
import os
from server.network.event_bus import EventBus

class SocketServer:
    def __init__(self):
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", 5050))
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.event_bus = EventBus()
        self.connected_clients = []

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"🚀 Socket Server running on {self.host}:{self.port} waiting for players...")

        try:
            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"🔌 New client connected: {addr}")
                self.connected_clients.append(client_socket)
                
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()
        except KeyboardInterrupt:
            print("\n🛑 Server shutting down.")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                payload = json.loads(message)
                print(f"📥 Received: {payload}")

                response = self.event_bus.handle_message(client_socket, payload)

                client_socket.send(json.dumps(response).encode('utf-8'))

            except Exception as e:
                print(f"⚠️ Connection error with client: {e}")
                break

        print("❌ Client disconnected.")
        if client_socket in self.connected_clients:
            self.connected_clients.remove(client_socket)
        client_socket.close()
