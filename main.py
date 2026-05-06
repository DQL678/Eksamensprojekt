import pygame
import os
from map import GameMap
from player import Player
from weapons import WeaponDrop, Projectile, LaserBeam, create_weapon_from_json, load_weapon_images
import weapons
from client import NetworkClient


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, screen, font):
        pygame.draw.rect(screen,(80, 80, 80), self.rect)
        pygame.draw.rect(screen,(230, 230, 230), self.rect,2)

        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Slider:
    def __init__(self, x, y, width, min_value, max_value, start_value, label):
        self.x = x
        self.y = y
        self.width = width
        self.min_value = min_value
        self.max_value = max_value
        self.value = start_value
        self.label = label
        self.bar_rect = pygame.Rect(x, y, width, 6)
        self.handle_radius = 12
        self.dragging = False

    def get_handle_x(self):
        percent = (self.value - self.min_value) / (self.max_value - self.min_value)
        return self.x + int(percent * self.width)

    def handle_event(self, event):
        handle_x = self.get_handle_x()
        handle_rect = pygame.Rect(
            handle_x - self.handle_radius,
            self.y - self.handle_radius,
            self.handle_radius * 2,
            self.handle_radius * 2
        )

        if event.type == pygame.MOUSEBUTTONDOWN:
            if handle_rect.collidepoint(event.pos) or self.bar_rect.collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_value(event.pos[0])

    def update_value(self, cursor_x):
        cursor_x = max(self.x, min(cursor_x, self.x + self.width))
        percent = (cursor_x - self.x) / self.width
        self.value = int(self.min_value + percent * (self.max_value - self.min_value))

    def draw(self, screen, font):
        text_surface = font.render(f"{self.label}: {self.value}", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y - 30))
        screen.blit(text_surface, text_rect)

        pygame.draw.rect(screen,(170, 170, 170), self.bar_rect)
        pygame.draw.circle(screen,(240, 240, 240),(self.get_handle_x(), self.y + 3), self.handle_radius)


class TextInput:
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key != pygame.K_RETURN:
                self.text += event.unicode

    def draw(self, screen, font):
        color = (255, 255, 255) if self.active else (180, 180, 180)

        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, color, self.rect, 2)

        display = self.text if self.text else self.placeholder
        text_color = (255, 255, 255) if self.text else (120, 120, 120)

        surf = font.render(display, True, text_color)
        screen.blit(surf, (self.rect.x + 10, self.rect.centery - surf.get_height() // 2))


PROJECTILE_COLORS = {
    "Sniper": (40, 40, 180),
    "Shotgun": (180, 120, 20),
    "Assault Rifle": (40, 150, 70),
    "Minigun": (130, 40, 150),
    "Freeze Gun": (80, 220, 255),
    "Snowball Cannon": (180, 240, 255),
    "Laserbeamer": (255, 0, 0),
}

DEFAULT_PROJECTILE_COLOR = (200, 0, 0)

WEAPON_SIZES = {
    "Handgun": (60, 50),
    "Sniper": (120, 30),
    "Shotgun": (100, 25),
    "Assault Rifle": (130, 55),
    "Minigun": (100, 40),
    "Freeze Gun": (80, 45),
    "Laserbeamer": (110, 40),
    "Snowball Cannon": (100, 50)
}


class GameApp:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen_width = 1200
        self.screen_height = 700

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height),pygame.RESIZABLE)
        pygame.display.set_caption("Gun Man Game")

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.base_width = 1600
        self.base_height = 900

        self.resize_ui()

        self.music_loaded = False
        self.load_background_music()

        self.game_map = None
        self.player = None
        self.weapon_drop = None

        self.server_projectiles = []
        self.pending_projectiles = []

        self.weapon_delay = 5000
        self.last_weapon_removed_time = 0
        self.mouse_held = False

        self.network = None
        self.other_players = {}
        self.picked_up_weapon_flag = False
        self.connection_error = ""

        self.local_projectiles = []

        self.game_over = False
        self.winner_id = None

        load_weapon_images()

        self.pistol_sound = pygame.mixer.Sound("Lydfiler/Pistol.mp3")
        self.shotgun_sound = pygame.mixer.Sound("Lydfiler/Shotgun.mp3")
        self.minigun_sound = pygame.mixer.Sound("Lydfiler/Minigun.mp3")
        self.laser_sound = pygame.mixer.Sound("Lydfiler/Laser.mp3")
        self.freezegun_sound = pygame.mixer.Sound("Lydfiler/Freezegun.mp3")
        self.snowball_sound = pygame.mixer.Sound("Lydfiler/SnowballCannon.mp3")
        self.assault_rifle_sound = pygame.mixer.Sound("Lydfiler/AssaultRifle.mp3")
        self.sniper_sound = pygame.mixer.Sound("Lydfiler/Sniper.mp3")
        self.minigun_channel = None
        self.minigun_sound_playing = False

    def load_background_music(self):
        music_path = os.path.join(
            os.path.dirname(__file__), "Lydfiler/Masked Dedede - Kirby Triple Deluxe Music Extended.mp3")

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.music_slider.value / 100)
            pygame.mixer.music.play(-1)
            self.music_loaded = True
        except Exception as error:
            print("Kunne ikke indlæse musik:", error)
            self.music_loaded = False

    def center_horizontally(self, width):
        return self.screen_width // 2 - width // 2

    def resize_ui(self):
        scale = max(0.6, min(self.screen_height / 900, 1.5))

        self.title_font = pygame.font.SysFont("arial", int(56 * scale), bold=True)
        self.button_font = pygame.font.SysFont("arial", int(28 * scale))
        self.text_font = pygame.font.SysFont("arial", int(24 * scale))
        self.small_font = pygame.font.SysFont("arial", int(22 * scale))

        button_width = int(self.screen_width * 0.25)
        button_height = int(self.screen_height * 0.08)
        button_x = self.center_horizontally(button_width)

        self.join_button = Button(button_x, int(self.screen_height * 0.30), button_width, button_height, "Join Game")
        self.settings_button = Button(button_x, int(self.screen_height * 0.42), button_width, button_height, "Settings")
        self.quit_button = Button(button_x, int(self.screen_height * 0.54), button_width, button_height, "Quit")
        self.back_button = Button(button_x, int(self.screen_height * 0.70), button_width, button_height, "Tilbage")

        self.map1_button = Button(button_x, int(self.screen_height * 0.34), button_width, button_height, "Map 1")
        self.map2_button = Button(button_x, int(self.screen_height * 0.46), button_width, button_height, "Map 2")

        input_width = int(self.screen_width * 0.3)
        input_x = self.center_horizontally(input_width)

        self.ip_input = TextInput( input_x,int(self.screen_height * 0.40),input_width, 44,"Server IP (f.eks. 192.168.1.5)" )

        self.connect_button = Button(button_x, int(self.screen_height * 0.54), button_width, button_height, "Forbind")

        slider_width = int(self.screen_width * 0.3)
        slider_x = self.center_horizontally(slider_width)

        self.music_slider = Slider(slider_x, int(self.screen_height * 0.40), slider_width, 0, 100, 50, "Music volume")
        self.sfx_slider = Slider(slider_x, int(self.screen_height * 0.53), slider_width, 0, 100, 50, "SFX volume")

    def start_game(self, map_number):
        self.game_map = GameMap(self.base_width, self.base_height, map_number)

        spawn = self.game_map.spawn_points[0]
        self.player = Player(spawn[0], spawn[1], 40, 60, (255, 255, 255))

        self.weapon_drop = None
        self.server_projectiles = []
        self.local_projectiles = []
        self.other_players = {}
        self.pending_projectiles = []
        self.picked_up_weapon_flag = False
        self.last_weapon_removed_time = pygame.time.get_ticks()
        self.mouse_held = False
        self.connection_error = ""

        self.game_over = False
        self.winner_id = None

        self.stop_minigun_sound()

        self.state = "game"

    def try_connect(self):
        ip = self.ip_input.text.strip()

        if not ip:
            self.connection_error = "Indtast en IP-adresse"
            return

        try:
            self.network = NetworkClient(ip)
            self.connection_error = ""
            self.state = "map_select"
        except Exception as e:
            self.network = None
            self.connection_error = f"Kunne ikke forbinde: {e}"

    def select_map(self, requested_map):
        if not self.network:
            self.start_game(requested_map)
            return

        data = {"selected_map_request": requested_map}

        response = self.network.send_player_data(data)

        if response is None:
            self.connection_error = "Kunne ikke vælge map"
            self.state = "menu"
            return

        map_to_start = response.get("selected_map", requested_map)

        if map_to_start is None:
            map_to_start = requested_map

        self.start_game(map_to_start)

    def spawn_weapon(self):
        self.weapon_drop = WeaponDrop(self.base_width)

    def remove_weapon(self):
        self.weapon_drop = None
        self.last_weapon_removed_time = pygame.time.get_ticks()

    def update_weapons_local(self):
        now = pygame.time.get_ticks()

        if self.weapon_drop is None:
            if now - self.last_weapon_removed_time > self.weapon_delay:
                self.spawn_weapon()
        else:
            self.weapon_drop.update()

            if self.weapon_drop.is_picked_up(self.player):
                self.player.pick_up_weapon(self.weapon_drop)
                self.remove_weapon()

            elif self.weapon_drop.is_out_of_map(self.base_height):
                self.remove_weapon()

    def apply_server_weapon_drop(self, drop_data):
        if drop_data is None:
            self.weapon_drop = None
            return

        if self.weapon_drop is None:
            self.weapon_drop = WeaponDrop.__new__(WeaponDrop)
            self.weapon_drop.width = 30
            self.weapon_drop.height = 20
            self.weapon_drop.y_velocity = 0
            self.weapon_drop.gravity = 0.18
            self.weapon_drop.max_fall_speed = 4

            try:
                self.weapon_drop.weapon = create_weapon_from_json(drop_data["weapon"])
            except Exception:
                self.weapon_drop = None
                return

        self.weapon_drop.x = drop_data["x"]
        self.weapon_drop.y = drop_data["y"]
        self.weapon_drop.rect = pygame.Rect(drop_data["x"], drop_data["y"], 30, 20)

    def set_sound_volume(self):
        volume = self.sfx_slider.value / 100

        self.pistol_sound.set_volume(volume)
        self.shotgun_sound.set_volume(volume)
        self.minigun_sound.set_volume(volume)
        self.laser_sound.set_volume(volume)
        self.freezegun_sound.set_volume(volume)
        self.snowball_sound.set_volume(volume)
        self.assault_rifle_sound.set_volume(volume)
        self.sniper_sound.set_volume(volume)

    def stop_minigun_sound(self):
        if self.minigun_sound_playing:
            if self.minigun_channel:
                self.minigun_channel.stop()

            self.minigun_channel = None
            self.minigun_sound_playing = False

    def play_shoot_sound(self, weapon):
        self.set_sound_volume()

        if weapon.name == "Handgun":
            self.pistol_sound.play()

        elif weapon.name == "Shotgun":
            self.shotgun_sound.play()

        elif weapon.name == "Laserbeamer":
            self.laser_sound.play()

        elif weapon.name == "Freeze Gun":
            self.freezegun_sound.play()

        elif weapon.name == "Snowball Cannon":
            self.snowball_sound.play()

        elif weapon.name == "Assault Rifle":
            self.assault_rifle_sound.play()

        elif weapon.name == "Sniper":
            self.sniper_sound.play()

        elif weapon.name == "Minigun":
            if not self.minigun_sound_playing:
                self.minigun_channel = self.minigun_sound.play(-1)
                self.minigun_sound_playing = True

    def shoot(self):
        if not self.player:
            return

        now = pygame.time.get_ticks()
        projectile_data_list = self.player.try_shoot(now)

        if not projectile_data_list:
            return

        weapon = self.player.current_weapon

        self.play_shoot_sound(weapon)

        if weapon.name == "Laserbeamer":
            data = projectile_data_list[0]

            if not self.network:
                beam = LaserBeam(
                    data["x"],
                    data["y"],
                    self.player.direction,
                    weapon,
                    self.game_map.platforms,
                    self.base_width
                )
                self.local_projectiles.append(beam)

            else:
                self.pending_projectiles.append({
                    "x": data["x"],
                    "y": data["y"],
                    "dir": self.player.direction,
                    "speed": 0,
                    "range": weapon.special_duration,
                    "distance": 0,
                    "y_speed": 0,
                    "is_laser": True,
                    "weapon": weapon.name,
                    "damage": weapon.projectile_damage,
                    "size": weapon.projectile_size,
                    "special_type": weapon.special_type,
                    "special_duration": weapon.special_duration,
                    "special_amount": weapon.special_amount,
                })

            return

        count = len(projectile_data_list)

        for i, data in enumerate(projectile_data_list):
            spread = (i - count // 2) * 2 if weapon.name == "Shotgun" else 0

            if not self.network:
                proj = Projectile(data["x"], data["y"], self.player.direction, weapon, spread)
                self.local_projectiles.append(proj)

            else:
                self.pending_projectiles.append({
                    "x": data["x"],
                    "y": data["y"],
                    "dir": self.player.direction,
                    "speed": weapon.projectile_speed,
                    "range": weapon.projectile_range,
                    "distance": 0,
                    "y_speed": spread,
                    "is_laser": False,
                    "weapon": weapon.name,
                    "damage": weapon.projectile_damage,
                    "size": weapon.projectile_size,
                    "special_type": weapon.special_type,
                    "special_duration": weapon.special_duration,
                    "special_amount": weapon.special_amount,
                })

    def update_auto_fire(self):
        if not self.player:
            self.stop_minigun_sound()
            return

        if not self.mouse_held:
            self.stop_minigun_sound()
            return

        if self.player.current_weapon is None:
            self.stop_minigun_sound()
            return

        if self.player.current_weapon.name == "Minigun":
            if self.player.ammo <= 0:
                self.stop_minigun_sound()
                return

            self.shoot()

        elif self.player.current_weapon.name == "Laserbeamer":
            self.stop_minigun_sound()
            self.shoot()

        else:
            self.stop_minigun_sound()

    def update_local_projectiles(self):
        remove = []

        for projectile in self.local_projectiles:
            projectile.update()

            if projectile.has_reached_max_range():
                remove.append(projectile)
                continue

            if projectile.is_laser:
                continue

            for platform in self.game_map.platforms:
                if projectile.rect.colliderect(platform):
                    remove.append(projectile)
                    break

        for projectile in remove:
            if projectile in self.local_projectiles:
                self.local_projectiles.remove(projectile)

    def sync_with_server(self):
        weapon_name = self.player.current_weapon.name if self.player.current_weapon else None

        data = {
            "x": self.player.x,
            "y": self.player.y,
            "direction": self.player.direction,
            "weapon": weapon_name,
            "ammo": self.player.ammo,
            "new_projectiles": self.pending_projectiles,
            "picked_up_weapon": self.picked_up_weapon_flag,
        }

        self.pending_projectiles = []
        self.picked_up_weapon_flag = False

        response = self.network.send_player_data(data)

        if response is None:
            return

        my_pid = self.network.player_id

        self.game_over = response.get("game_over", False)
        self.winner_id = response.get("winner_id")

        self.other_players = {}

        for pid_str, pdata in response["players"].items():
            if int(pid_str) == my_pid:
                self.player.rect.x = int(pdata.get("x", self.player.rect.x))
                self.player.rect.y = int(pdata.get("y", self.player.rect.y))
                self.player.x = self.player.rect.x
                self.player.y = self.player.rect.y

                self.player.hitpoints = pdata.get("hitpoints", self.player.hitpoints)
                self.player.lives = pdata.get("lives", self.player.lives)
                self.player.score = pdata.get("score", self.player.score)

                current_time = pygame.time.get_ticks()
                server_time_now = response.get("server_time", 0)

                frozen_until = pdata.get("frozen_until", 0)
                slowed_until = pdata.get("slowed_until", 0)
                slow_amount = pdata.get("slow_amount", 0)

                if frozen_until > server_time_now:
                    time_left = int((frozen_until - server_time_now) * 1000)
                    self.player.freeze(time_left, current_time)

                if slowed_until > server_time_now:
                    time_left = int((slowed_until - server_time_now) * 1000)
                    self.player.apply_slow(time_left, slow_amount, current_time)

                if self.player.lives <= 0:
                    self.stop_minigun_sound()
                    self.state = "game_over"

            else:
                self.other_players[pid_str] = pdata

        self.apply_server_weapon_drop(response.get("weapon_drop"))

        if self.weapon_drop is not None and self.weapon_drop.is_picked_up(self.player):
            self.player.pick_up_weapon(self.weapon_drop)
            self.weapon_drop = None
            self.picked_up_weapon_flag = True

        self.server_projectiles = response.get("projectiles", [])

        if self.game_over:
            self.stop_minigun_sound()
            self.state = "game_over"

    def update_game(self):
        keys = pygame.key.get_pressed()

        self.player.move(keys, self.game_map.platforms, self.base_width, self.base_height)
        self.player.update_reload(pygame.time.get_ticks())

        if self.network:
            self.sync_with_server()
        else:
            self.update_weapons_local()
            self.update_local_projectiles()

        self.update_auto_fire()

    def draw_server_projectiles(self, surface):
        for projectile in self.server_projectiles:
            if projectile.get("is_laser"):
                x = int(projectile["x"])
                y = int(projectile["y"])
                direction = projectile.get("dir", 1)
                end_x = self.base_width if direction == 1 else 0
                size = max(1, int(projectile.get("size", 4)))

                pygame.draw.line(surface, (255, 0, 0), (x, y), (end_x, y), size)

            else:
                size = max(1, int(projectile.get("size", 6)))
                x = int(projectile["x"])
                y = int(projectile["y"])

                color = PROJECTILE_COLORS.get(projectile.get("weapon", ""),DEFAULT_PROJECTILE_COLOR)

                pygame.draw.rect(surface, color, pygame.Rect(x, y, size, size))

    def draw_other_players(self, surface):
        for pid, pdata in self.other_players.items():
            if pdata.get("lives", 1) <= 0:
                continue
            x = int(pdata.get("x", 0))
            y = int(pdata.get("y", 0))

            rect = pygame.Rect(x, y, 40, 60)
            pygame.draw.rect(surface, (255, 80, 80), rect)

            label = self.small_font.render(f"P{pid}", True, (0, 0, 0))
            surface.blit(label, (x, y - 22))

            weapon_name = pdata.get("weapon")

            if weapon_name:
                img = weapons.WEAPON_IMAGES.get(weapon_name)

                if img:
                    width, height = WEAPON_SIZES.get(weapon_name, (50, 30))
                    scaled = pygame.transform.scale(img, (width, height))
                    direction = pdata.get("direction", 1)

                    if direction == -1:
                        scaled = pygame.transform.flip(scaled, True, False)
                        weapon_x = x - width + 30
                    else:
                        weapon_x = x + 40 - 30

                    weapon_y = y + 30 - height // 2
                    surface.blit(scaled, (weapon_x, weapon_y))

    def draw_game(self):
        surface = pygame.Surface((self.base_width, self.base_height))

        self.game_map.draw(surface)
        self.draw_other_players(surface)
        self.player.draw(surface)

        if self.weapon_drop:
            self.weapon_drop.draw(surface)

        if self.network:
            self.draw_server_projectiles(surface)
        else:
            for projectile in self.local_projectiles:
                projectile.draw(surface)

        scaled = pygame.transform.scale(surface,(self.screen_width, self.screen_height))
        self.screen.blit(scaled, (0, 0))

        self.draw_game_info()

    def draw_game_info(self):
        hp_text = self.small_font.render(
            f"HP: {self.player.hitpoints} / 100   Lives: {self.player.lives}",
            True,
            (0, 0, 0)
        )
        self.screen.blit(hp_text, (20, 20))

        bar_x = 20
        bar_y = 48
        bar_width = 200
        bar_height = 18

        pygame.draw.rect(self.screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))

        hp_percent = max(0, min(self.player.hitpoints / 100, 1))
        current_bar_width = int(bar_width * hp_percent)

        pygame.draw.rect(self.screen, (40, 200, 60), (bar_x, bar_y, current_bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)

        score_text = self.small_font.render(f"Score: {self.player.score}",True,(0, 0, 0))
        self.screen.blit(score_text, (20, 75))

        if self.player.current_weapon is None:
            weapon_text = self.small_font.render("Weapon: None", True, (0, 0, 0))
            ammo_text = self.small_font.render("Ammo: 0", True, (0, 0, 0))
        else:
            weapon_text = self.small_font.render(f"Weapon: {self.player.current_weapon.name}", True, (0, 0, 0))
            ammo_text = self.small_font.render(f"Ammo: {self.player.ammo}", True, (0, 0, 0))

        self.screen.blit(weapon_text, (20, 105))
        self.screen.blit(ammo_text, (20, 130))

        if self.network:
            mp_text = self.small_font.render(
                f"Online – Spiller {self.network.player_id} | Øvrige: {len(self.other_players)}",
                True,
                (124,252,0)
            )
            self.screen.blit(mp_text, (20, self.screen_height - 35))

    def draw_game_over(self):
        self.screen.fill((20, 20, 20))

        my_id = self.network.player_id if self.network else None

        if self.winner_id == my_id:
            title_text = "YOU WON!"
            color = (80, 220, 80)
        else:
            title_text = "GAME OVER"
            color = (220, 60, 60)

        title = self.title_font.render(title_text, True, color)
        title_rect = title.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.35)))
        self.screen.blit(title, title_rect)
        if self.game_over:
            info_text = "Tryk på ESC-tasten for at gå tilbage til Menu."
        else:
            info_text = "Du har tabt spillet. Vent på at runden bliver færdig."

        info = self.text_font.render(info_text,True,(255, 255, 255))
        info_rect = info.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.50)))
        self.screen.blit(info, info_rect)

    def draw_menu(self):
        self.screen.fill((25, 25, 25))

        title = self.title_font.render("Gun Man Game", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.18)))
        self.screen.blit(title, title_rect)

        self.join_button.draw(self.screen, self.button_font)
        self.settings_button.draw(self.screen, self.button_font)
        self.quit_button.draw(self.screen, self.button_font)

    def draw_join_screen(self):
        self.screen.fill((25, 25, 25))

        title = self.title_font.render("Join Game", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.18)))
        self.screen.blit(title, title_rect)

        label = self.text_font.render("Server IP-adresse:", True, (200, 200, 200))
        self.screen.blit(label, (self.ip_input.rect.x, self.ip_input.rect.y - 32))

        self.ip_input.draw(self.screen, self.text_font)
        self.connect_button.draw(self.screen, self.button_font)
        self.back_button.draw(self.screen, self.button_font)

        if self.connection_error:
            error_text = self.text_font.render(self.connection_error, True, (220, 60, 60))
            error_rect = error_text.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.65)))
            self.screen.blit(error_text, error_rect)

    def draw_map_select(self):
        self.screen.fill((25, 25, 25))

        title = self.title_font.render("Vælg Map", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.18)))
        self.screen.blit(title, title_rect)

        self.map1_button.draw(self.screen, self.button_font)
        self.map2_button.draw(self.screen, self.button_font)

    def draw_settings(self):
        self.screen.fill((40, 40, 60))

        title = self.title_font.render("Settings", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.16)))
        self.screen.blit(title, title_rect)

        self.music_slider.draw(self.screen, self.text_font)
        self.sfx_slider.draw(self.screen, self.text_font)
        self.back_button.draw(self.screen, self.button_font)

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.stop_minigun_sound()

                if self.network:
                    self.network.close()
                    self.network = None

                self.state = "menu"

            if event.key == pygame.K_r:
                self.player.start_reload(pygame.time.get_ticks())

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_held = True

            if self.player.current_weapon is not None:
                if self.player.current_weapon.name not in ("Minigun", "Laserbeamer"):
                    self.shoot()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_held = False
            self.stop_minigun_sound()

    def handle_game_over_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game_over:
                    if self.network:
                        self.network.close()
                        self.network = None

                    self.state = "menu"

    def run(self):
        while self.running:
            self.clock.tick(60)

            if self.music_loaded:
                pygame.mixer.music.set_volume(self.music_slider.value / 100)

            self.set_sound_volume()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_minigun_sound()
                    self.running = False

                if event.type == pygame.VIDEORESIZE:
                    self.screen_width = event.w
                    self.screen_height = event.h
                    self.screen = pygame.display.set_mode((event.w, event.h),pygame.RESIZABLE)
                    self.resize_ui()

                if self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.join_button.is_clicked(event.pos):
                            self.state = "join_screen"
                        elif self.settings_button.is_clicked(event.pos):
                            self.state = "settings"
                        elif self.quit_button.is_clicked(event.pos):
                            self.stop_minigun_sound()
                            self.running = False

                elif self.state == "join_screen":
                    self.ip_input.handle_event(event)

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.connect_button.is_clicked(event.pos):
                            self.try_connect()
                        elif self.back_button.is_clicked(event.pos):
                            self.state = "menu"

                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.try_connect()

                elif self.state == "map_select":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.map1_button.is_clicked(event.pos):
                            self.select_map(1)
                        elif self.map2_button.is_clicked(event.pos):
                            self.select_map(2)

                elif self.state == "settings":
                    self.music_slider.handle_event(event)
                    self.sfx_slider.handle_event(event)

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.back_button.is_clicked(event.pos):
                            self.state = "menu"

                elif self.state == "game":
                    self.handle_game_events(event)

                elif self.state == "game_over":
                    self.handle_game_over_events(event)

            if self.state == "game":
                self.update_game()

            elif self.state == "game_over":
                self.stop_minigun_sound()

                if self.network and self.player:
                    self.sync_with_server()

            else:
                self.stop_minigun_sound()

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "join_screen":
                self.draw_join_screen()
            elif self.state == "map_select":
                self.draw_map_select()
            elif self.state == "settings":
                self.draw_settings()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()

            pygame.display.update()

        self.stop_minigun_sound()

        if self.network:
            self.network.close()

        pygame.quit()


if __name__ == "__main__":
    GameApp().run()