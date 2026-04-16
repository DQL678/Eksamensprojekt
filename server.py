import socket
import threading
import json
import random
import time

HOST = "0.0.0.0"
PORT = 5555

players = {}
weapon_drop = None
last_weapon_spawn = time.time()
weapon_delay = 5
next_player_id = 1

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server started...")

lock = threading.Lock()

def update_weapon_drop():
    global weapon_drop, last_weapon_spawn

    now = time.time()

    if weapon_drop is None:
        if now - last_weapon_spawn >= weapon_delay:
            weapon_drop = {
                "x": random.randint(50, 1550),
                "y": 0,
                "speed": 4
            }
            last_weapon_spawn = now
    else:
        weapon_drop["y"] += weapon_drop["speed"]

        if weapon_drop["y"] > 900:
            weapon_drop = None
            last_weapon_spawn = now

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

                update_weapon_drop()

                response = {
                    "your_id": player_id,
                    "players": players,
                    "weapon_drop": weapon_drop
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