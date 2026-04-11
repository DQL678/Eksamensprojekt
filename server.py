import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5555

players = {}
next_player_id = 1

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server started...")

lock = threading.Lock()


def handle_client(conn, addr, player_id):
    global players

    print(f"Player {player_id} connected from {addr}")

    players[player_id] = {
        "x": 100,
        "y": 100
    }

    conn.send(str(player_id).encode())

    try:
        while True:
            data = conn.recv(1024).decode()

            if not data:
                break

            player_data = json.loads(data)

            with lock:
                players[player_id] = player_data

                response = {
                    "your_id": player_id,
                    "players": players
                }

                conn.send(json.dumps(response).encode())

    except:
        print(f"Player {player_id} disconnected")

    finally:
        with lock:
            if player_id in players:
                del players[player_id]

        conn.close()

while True:
    conn, addr = server.accept()

    player_id = next_player_id
    next_player_id += 1

    thread = threading.Thread(
        target=handle_client,
        args=(conn, addr, player_id)
    )
    thread.start()