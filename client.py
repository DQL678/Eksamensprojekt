import socket
import json

class NetworkClient:
    def __init__(self, host, port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        self.player_id = int(self.client.recv(1024).decode())

    def send_player_data(self, data):
        self.client.send(json.dumps(data).encode())

        response = self.client.recv(4096).decode()
        return json.loads(response)