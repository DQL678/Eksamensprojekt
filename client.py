import socket
import json


class NetworkClient:

    def __init__(self, host, port=5555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(5.0)

        print(f"Forbinder til {host}:{port}...")
        self.client.connect((host, port))
        self.client.settimeout(None)  # Fjern timeout efter forbindelse

        raw = b""
        while b"\n" not in raw:
            raw += self.client.recv(64)

        self.player_id = int(raw.decode().strip())
        print("Forbundet som spiller:", self.player_id)

        self.buffer = ""

    def send_player_data(self, data):
        try:
            packet = json.dumps(data) + "\n"
            self.client.send(packet.encode())

            # Modtag svar
            while "\n" not in self.buffer:
                chunk = self.client.recv(8192).decode()
                if not chunk:
                    return None
                self.buffer += chunk

            line, self.buffer = self.buffer.split("\n", 1)
            return json.loads(line)

        except Exception as e:
            print("Netværksfejl:", e)
            return None

    def close(self):
        try:
            self.client.close()
        except:
            pass