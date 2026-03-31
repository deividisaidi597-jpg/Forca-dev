import socket
import json

class SocketClient:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def send(self, data):
        self.client.send(json.dumps(data).encode())

    def receive(self):
        return self.client.recv(1024).decode()