import socket
import threading
import json
import random
import time

HOST = "0.0.0.0"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

print("SERVER RUNNING på port", PORT)

players = {}
projectiles = []
weapon_drop = None
weapon_drop_timer = 0
WEAPON_DELAY = 5.0  # sekunder mellem weapon drops

lock = threading.Lock()
next_id = 1

WEAPON_NAMES = [
    "Handgun", "Sniper", "Shotgun",
    "Assault Rifle", "Minigun", "Freeze Gun",
    "Laserbeamer", "Snowball Cannon"
]


def get_time():
    return time.time()


def maybe_spawn_weapon():
    global weapon_drop, weapon_drop_timer

    if weapon_drop is None:
        now = get_time()
        if now - weapon_drop_timer >= WEAPON_DELAY:
            weapon_drop = {
                "x": random.randint(100, 1500),
                "y": -40,
                "weapon": random.choice(WEAPON_NAMES),
                "y_velocity": 0
            }


def update_weapon():
    global weapon_drop

    if weapon_drop is None:
        return

    # Simpel tyngdekraft
    weapon_drop["y_velocity"] = min(
        weapon_drop.get("y_velocity", 0) + 0.18,
        4
    )
    weapon_drop["y"] += weapon_drop["y_velocity"]

    if weapon_drop["y"] > 920:
        remove_weapon()


def remove_weapon():
    global weapon_drop, weapon_drop_timer
    weapon_drop = None
    weapon_drop_timer = get_time()


def update_projectiles():
    global projectiles
    remove = []

    for p in projectiles:
        p["x"] += p["dir"] * p["speed"]
        p["y"] += p.get("y_speed", 0)
        p["distance"] += abs(p["speed"])

        if p["distance"] >= p["range"]:
            remove.append(p)

    for p in remove:
        if p in projectiles:
            projectiles.remove(p)


def build_response():
    return {
        "players": players,
        "projectiles": projectiles,
        "weapon_drop": weapon_drop
    }


def handle_client(conn, addr, pid):
    global players, projectiles, weapon_drop

    print(f"FORBUNDET: {addr} som spiller {pid}")

    with lock:
        players[pid] = {
            "x": 100,
            "y": 800,
            "direction": 1,
            "weapon": None,
            "ammo": 0,
            "hitpoints": 100,
            "lives": 3,
            "score": 0
        }

    # Send player ID
    conn.send((str(pid) + "\n").encode())

    buffer = ""

    while True:
        try:
            data = conn.recv(8192).decode()

            if not data:
                break

            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)

                if not line.strip():
                    continue

                player_data = json.loads(line)

                with lock:
                    # Opdater spillerens state
                    players[pid].update({
                        "x": player_data.get("x", players[pid]["x"]),
                        "y": player_data.get("y", players[pid]["y"]),
                        "direction": player_data.get("direction", 1),
                        "weapon": player_data.get("weapon"),
                        "ammo": player_data.get("ammo", 0),
                        "hitpoints": player_data.get("hitpoints", 100),
                        "lives": player_data.get("lives", 3),
                        "score": player_data.get("score", 0)
                    })

                    # Opdater spil-state
                    maybe_spawn_weapon()
                    update_weapon()
                    update_projectiles()

                    # Håndter skud fra klient
                    new_projectiles = player_data.get("new_projectiles", [])
                    for proj in new_projectiles:
                        proj["owner"] = pid
                        projectiles.append(proj)

                    # Håndter weapon pickup
                    if player_data.get("picked_up_weapon"):
                        remove_weapon()

                    response = build_response()

                conn.send((json.dumps(response) + "\n").encode())

        except Exception as e:
            print(f"FEJL for spiller {pid}:", e)
            break

    with lock:
        players.pop(pid, None)

    conn.close()
    print(f"AFBRUDT: spiller {pid}")


while True:
    conn, addr = server.accept()

    with lock:
        pid = next_id
        next_id += 1

    thread = threading.Thread(
        target=handle_client,
        args=(conn, addr, pid),
        daemon=True
    )
    thread.start()