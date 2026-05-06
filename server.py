import socket
import threading
import json
import random
import time


def get_my_lan_IP():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


HOST = "0.0.0.0"
PORT = 5555

BASE_WIDTH = 1600
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server.bind((HOST, PORT))
except OSError as e:
    print(f"FEJL: Kunne ikke starte server på port {PORT}: {e}")
    print("Løsning: Åbn terminal og kør:  kill $(lsof -ti:5555)")
    exit(1)

server.listen()

IP = get_my_lan_IP()
print(f"SERVER KØRER på port {PORT}, IP: {IP}")

players = {}
projectiles = {}
next_proj_id = 1

weapon_drop = None
weapon_drop_timer = 0
WEAPON_DELAY = 5.0

lock = threading.Lock()
next_client_id = 1

TICK_RATE = 60

game_over = False
winner_id = None
selected_map = None

WEAPON_NAMES = [
    "Handgun", "Sniper", "Shotgun",
    "Assault Rifle", "Minigun", "Freeze Gun",
    "Laserbeamer", "Snowball Cannon"
]


def get_time():
    return time.time()


def get_random_spawn():
    return random.choice([
        (100, 800),
        (760, 800),
        (1400, 800)
    ])


def get_platforms_for_map(map_number):
    if map_number == 2:
        return [
            {"x": 0, "y": 860, "w": 1600, "h": 40},

            {"x": 650, "y": 130, "w": 300, "h": 8},

            {"x": 520, "y": 250, "w": 180, "h": 8},
            {"x": 900, "y": 250, "w": 180, "h": 8},

            {"x": 390, "y": 370, "w": 180, "h": 8},
            {"x": 1030, "y": 370, "w": 180, "h": 8},

            {"x": 260, "y": 490, "w": 180, "h": 8},
            {"x": 1160, "y": 490, "w": 180, "h": 8},

            {"x": 390, "y": 610, "w": 180, "h": 8},
            {"x": 1030, "y": 610, "w": 180, "h": 8},

            {"x": 520, "y": 730, "w": 180, "h": 8},
            {"x": 900, "y": 730, "w": 180, "h": 8},

            {"x": 650, "y": 820, "w": 300, "h": 8},
        ]

    return [
        {"x": 0, "y": 860, "w": 1600, "h": 40},

        {"x": 180, "y": 100, "w": 140, "h": 8},
        {"x": 700, "y": 100, "w": 200, "h": 8},
        {"x": 1280, "y": 100, "w": 140, "h": 8},

        {"x": 60, "y": 220, "w": 120, "h": 8},
        {"x": 420, "y": 220, "w": 160, "h": 8},
        {"x": 1020, "y": 220, "w": 160, "h": 8},
        {"x": 1380, "y": 220, "w": 120, "h": 8},

        {"x": 140, "y": 340, "w": 140, "h": 8},
        {"x": 700, "y": 340, "w": 200, "h": 8},
        {"x": 1320, "y": 340, "w": 140, "h": 8},

        {"x": 40, "y": 460, "w": 120, "h": 8},
        {"x": 390, "y": 460, "w": 160, "h": 8},
        {"x": 1050, "y": 460, "w": 160, "h": 8},
        {"x": 1400, "y": 460, "w": 120, "h": 8},

        {"x": 180, "y": 580, "w": 140, "h": 8},
        {"x": 700, "y": 580, "w": 200, "h": 8},
        {"x": 1280, "y": 580, "w": 140, "h": 8},

        {"x": 60, "y": 700, "w": 120, "h": 8},
        {"x": 420, "y": 700, "w": 160, "h": 8},
        {"x": 1020, "y": 700, "w": 160, "h": 8},
        {"x": 1380, "y": 700, "w": 120, "h": 8},

        {"x": 180, "y": 820, "w": 140, "h": 8},
        {"x": 700, "y": 820, "w": 200, "h": 8},
        {"x": 1280, "y": 820, "w": 140, "h": 8},
    ]


def reset_round():
    global projectiles, weapon_drop, weapon_drop_timer
    global game_over, winner_id, next_proj_id
    global next_client_id, selected_map

    projectiles = {}
    next_proj_id = 1

    weapon_drop = None
    weapon_drop_timer = get_time()

    game_over = False
    winner_id = None

    selected_map = None
    next_client_id = 1


def choose_map(requested_map):
    global selected_map

    if selected_map is None:
        selected_map = requested_map

    return selected_map


def rects_collide(a, b):
    return (
        a["x"] < b["x"] + b["w"] and
        a["x"] + a["w"] > b["x"] and
        a["y"] < b["y"] + b["h"] and
        a["y"] + a["h"] > b["y"]
    )


def projectile_hits_platform(projectile_rect):
    platforms = get_platforms_for_map(selected_map or 1)

    for platform in platforms:
        if rects_collide(projectile_rect, platform):
            return True

    return False


def find_laser_end_x(start_x, y, direction, size):
    platforms = get_platforms_for_map(selected_map or 1)

    if direction == 1:
        end_x = BASE_WIDTH
        closest_distance = BASE_WIDTH

        for platform in platforms:
            laser_top = y - size // 2
            laser_bottom = y + size // 2

            if laser_bottom >= platform["y"] and laser_top <= platform["y"] + platform["h"]:
                if platform["x"] > start_x:
                    distance = platform["x"] - start_x

                    if distance < closest_distance:
                        closest_distance = distance
                        end_x = platform["x"]

        return end_x

    else:
        end_x = 0
        closest_distance = BASE_WIDTH

        for platform in platforms:
            laser_top = y - size // 2
            laser_bottom = y + size // 2

            if laser_bottom >= platform["y"] and laser_top <= platform["y"] + platform["h"]:
                platform_right = platform["x"] + platform["w"]

                if platform_right < start_x:
                    distance = start_x - platform_right

                    if distance < closest_distance:
                        closest_distance = distance
                        end_x = platform_right

        return end_x


def check_game_over():
    global game_over, winner_id

    alive_players = []

    for player_id, player in players.items():
        if player["lives"] > 0:
            alive_players.append(player_id)

    if len(players) >= 2 and len(alive_players) == 1:
        game_over = True
        winner_id = alive_players[0]


def apply_special_effect(target_id, projectile):
    if target_id not in players:
        return

    special_type = projectile.get("special_type")
    special_duration = projectile.get("special_duration", 0)
    special_amount = projectile.get("special_amount", 0)

    if special_type == "freeze":
        players[target_id]["frozen_until"] = max(
            players[target_id].get("frozen_until", 0),
            get_time() + special_duration / 1000
        )

    if special_type == "slow":
        players[target_id]["slowed_until"] = max(
            players[target_id].get("slowed_until", 0),
            get_time() + special_duration / 1000
        )
        players[target_id]["slow_amount"] = special_amount


def damage_player(target_id, damage, owner_id):
    if target_id not in players:
        return

    if players[target_id]["lives"] <= 0:
        return

    players[target_id]["hitpoints"] -= damage

    if players[target_id]["hitpoints"] <= 0:
        players[target_id]["lives"] -= 1

        if owner_id in players:
            players[owner_id]["score"] += 1

        if players[target_id]["lives"] <= 0:
            players[target_id]["hitpoints"] = 0
            check_game_over()
        else:
            spawn_x, spawn_y = get_random_spawn()

            players[target_id]["hitpoints"] = 100
            players[target_id]["x"] = spawn_x
            players[target_id]["y"] = spawn_y

            players[target_id]["frozen_until"] = 0
            players[target_id]["slowed_until"] = 0
            players[target_id]["slow_amount"] = 0

            players[target_id]["respawn_protection_until"] = get_time() + 0.5


def maybe_spawn_weapon():
    global weapon_drop, weapon_drop_timer

    if game_over:
        return

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

    if game_over:
        return

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

    if game_over:
        return

    remove_ids = []

    for proj_id, projectile in list(projectiles.items()):
        owner_id = projectile.get("owner")

        if projectile.get("is_laser"):
            age_ms = (get_time() - projectile["created_at"]) * 1000

            if age_ms >= projectile.get("range", 500):
                remove_ids.append(proj_id)
                continue

            direction = projectile.get("dir", 1)
            size = projectile.get("size", 8)

            end_x = find_laser_end_x(
                projectile["x"],
                projectile["y"],
                direction,
                size
            )

            projectile["end_x"] = end_x

            if direction == 1:
                laser_x = projectile["x"]
                laser_width = max(0, end_x - projectile["x"])
            else:
                laser_x = end_x
                laser_width = max(0, projectile["x"] - end_x)

            laser_rect = {
                "x": laser_x,
                "y": projectile["y"] - size // 2,
                "w": laser_width,
                "h": size
            }

            for player_id, player in players.items():
                if player_id == owner_id:
                    continue

                if player["lives"] <= 0:
                    continue

                player_rect = {
                    "x": player["x"],
                    "y": player["y"],
                    "w": PLAYER_WIDTH,
                    "h": PLAYER_HEIGHT
                }

                if rects_collide(laser_rect, player_rect):
                    damage_player(player_id, projectile.get("damage", 0), owner_id)
                    apply_special_effect(player_id, projectile)

            continue

        projectile["x"] += projectile["dir"] * projectile["speed"]
        projectile["y"] += projectile.get("y_speed", 0)
        projectile["distance"] += abs(projectile["speed"])

        projectile_rect = {
            "x": projectile["x"],
            "y": projectile["y"],
            "w": projectile.get("size", 8),
            "h": projectile.get("size", 8)
        }

        if projectile_hits_platform(projectile_rect):
            remove_ids.append(proj_id)
            continue

        if projectile["distance"] >= projectile["range"]:
            remove_ids.append(proj_id)
            continue

        for player_id, player in players.items():
            if player_id == owner_id:
                continue

            if player["lives"] <= 0:
                continue

            player_rect = {
                "x": player["x"],
                "y": player["y"],
                "w": PLAYER_WIDTH,
                "h": PLAYER_HEIGHT
            }

            if rects_collide(projectile_rect, player_rect):
                damage_player(player_id, projectile.get("damage", 0), owner_id)
                apply_special_effect(player_id, projectile)
                remove_ids.append(proj_id)
                break

    for proj_id in remove_ids:
        projectiles.pop(proj_id, None)


def game_loop():
    while True:
        start = get_time()

        with lock:
            maybe_spawn_weapon()
            update_weapon()
            update_projectiles()

        elapsed = get_time() - start
        sleep_time = (1.0 / TICK_RATE) - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)


def build_response():
    visible_players = {}

    for player_id, player in players.items():
        if player["lives"] > 0:
            visible_players[player_id] = player

    return {
        "players": visible_players,
        "projectiles": list(projectiles.values()),
        "weapon_drop": weapon_drop,
        "game_over": game_over,
        "winner_id": winner_id,
        "server_time": get_time(),
        "selected_map": selected_map
    }


def handle_client(conn, addr, cid):
    global players, projectiles, next_proj_id

    print(f"FORBUNDET: {addr} som spiller {cid}")

    spawn_x, spawn_y = get_random_spawn()

    with lock:
        players[cid] = {
            "x": spawn_x,
            "y": spawn_y,
            "direction": 1,
            "weapon": None,
            "ammo": 0,
            "hitpoints": 100,
            "lives": 3,
            "score": 0,
            "frozen_until": 0,
            "slowed_until": 0,
            "slow_amount": 0,
            "respawn_protection_until": 0
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
                    if "selected_map_request" in player_data:
                        choose_map(player_data["selected_map_request"])
                        response = build_response()
                        conn.send((json.dumps(response) + "\n").encode())
                        continue

                    if cid in players and players[cid]["lives"] > 0:
                        now = get_time()

                        if now > players[cid].get("respawn_protection_until", 0):
                            players[cid]["x"] = player_data.get("x", players[cid]["x"])
                            players[cid]["y"] = player_data.get("y", players[cid]["y"])

                        players[cid]["direction"] = player_data.get("direction", 1)
                        players[cid]["weapon"] = player_data.get("weapon")
                        players[cid]["ammo"] = player_data.get("ammo", 0)

                        if not game_over:
                            for projectile in player_data.get("new_projectiles", []):
                                projectile["owner"] = cid
                                projectile["id"] = next_proj_id

                                if projectile.get("is_laser"):
                                    projectile["created_at"] = get_time()

                                projectiles[next_proj_id] = projectile
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

        remove_ids = [
            proj_id for proj_id, projectile in projectiles.items()
            if projectile.get("owner") == cid
        ]

        for proj_id in remove_ids:
            projectiles.pop(proj_id, None)

        if len(players) == 0:
            reset_round()

    conn.close()
    print(f"AFBRUDT: spiller {cid}")


threading.Thread(target=game_loop, daemon=True).start()

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