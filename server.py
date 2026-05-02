import socket
import threading
import json
import random
import time

HOST = "0.0.0.0"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server.bind((HOST, PORT))
except OSError as e:
    print(f"FEJL: Kunne ikke starte server på port {PORT}: {e}")
    print("Løsning: Åbn terminal og kør:  kill $(lsof -ti:5555)")
    exit(1)

server.listen()
print(f"SERVER KØRER på port {PORT}")

players = {}
projectiles = {}  # proj_id -> projektil-dict
next_proj_id = 1
weapon_drop = None
weapon_drop_timer = 0
WEAPON_DELAY = 5.0

lock = threading.Lock()
next_client_id = 1

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
        if get_time() - weapon_drop_timer >= WEAPON_DELAY:
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
    weapon_drop["y_velocity"] = min(weapon_drop.get("y_velocity", 0) + 0.18, 4)
    weapon_drop["y"] += weapon_drop["y_velocity"]
    if weapon_drop["y"] > 920:
        remove_weapon()


def remove_weapon():
    global weapon_drop, weapon_drop_timer
    weapon_drop = None
    weapon_drop_timer = get_time()


def update_projectiles():
    global projectiles
    remove_ids = []
    for pid, p in projectiles.items():
        if p.get("is_laser"):
            # Lasere fjernes baseret på alder (duration i ms)
            age_ms = (get_time() - p["created_at"]) * 1000
            if age_ms >= p.get("range", 500):
                remove_ids.append(pid)
        else:
            p["x"] += p["dir"] * p["speed"]
            p["y"] += p.get("y_speed", 0)
            p["distance"] += abs(p["speed"])
            if p["distance"] >= p["range"]:
                remove_ids.append(pid)
    for pid in remove_ids:
        projectiles.pop(pid, None)


def build_response():
    return {
        "players": players,
        "projectiles": list(projectiles.values()),
        "weapon_drop": weapon_drop
    }


def handle_client(conn, addr, cid):
    global players, projectiles, next_proj_id, weapon_drop

    print(f"FORBUNDET: {addr} som spiller {cid}")

    with lock:
        players[cid] = {
            "x": 100, "y": 800,
            "direction": 1,
            "weapon": None, "ammo": 0,
            "hitpoints": 100, "lives": 3, "score": 0
        }

    conn.send((str(cid) + "\n").encode())

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
                    players[cid].update({
                        "x": player_data.get("x", players[cid]["x"]),
                        "y": player_data.get("y", players[cid]["y"]),
                        "direction": player_data.get("direction", 1),
                        "weapon": player_data.get("weapon"),
                        "ammo": player_data.get("ammo", 0),
                        "hitpoints": player_data.get("hitpoints", 100),
                        "lives": player_data.get("lives", 3),
                        "score": player_data.get("score", 0),
                    })

                    maybe_spawn_weapon()
                    update_weapon()
                    update_projectiles()

                    # Tilføj nye projektiler med unikke ID'er
                    for proj in player_data.get("new_projectiles", []):
                        proj["owner"] = cid
                        proj["id"] = next_proj_id
                        if proj.get("is_laser"):
                            proj["created_at"] = get_time()
                        projectiles[next_proj_id] = proj
                        next_proj_id += 1

                    if player_data.get("picked_up_weapon"):
                        remove_weapon()

                    response = build_response()

                conn.send((json.dumps(response) + "\n").encode())

        except Exception as e:
            print(f"FEJL for spiller {cid}:", e)
            break

    with lock:
        players.pop(cid, None)
        # Fjern spillerens projektiler når de disconnecter
        remove_ids = [pid for pid, p in projectiles.items() if p.get("owner") == cid]
        for pid in remove_ids:
            projectiles.pop(pid, None)

    conn.close()
    print(f"AFBRUDT: spiller {cid}")


while True:
    conn, addr = server.accept()
    with lock:
        cid = next_client_id
        next_client_id += 1
    thread = threading.Thread(
        target=handle_client,
        args=(conn, addr, cid),
        daemon=True
    )
    thread.start()