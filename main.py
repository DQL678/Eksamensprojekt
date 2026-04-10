import pygame
from map import GameMap
from player import Player
from weapons import WeaponDrop, Projectile


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, screen, font):
        pygame.draw.rect(screen, (80, 80, 80), self.rect)
        pygame.draw.rect(screen, (230, 230, 230), self.rect, 2)

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

    def update_value(self, mx):
        mx = max(self.x, min(mx, self.x + self.width))
        percent = (mx - self.x) / self.width
        self.value = int(self.min_value + percent * (self.max_value - self.min_value))

    def draw(self, screen, font):
        text_surface = font.render(f"{self.label}: {self.value}", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y - 30))
        screen.blit(text_surface, text_rect)

        pygame.draw.rect(screen, (170, 170, 170), self.bar_rect)
        pygame.draw.circle(
            screen,
            (240, 240, 240),
            (self.get_handle_x(), self.y + 3),
            self.handle_radius
        )


class GameApp:
    def __init__(self):
        pygame.init()

        self.screen_width = 1200
        self.screen_height = 700

        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption("Multiplayer Game")

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.base_width = 1600
        self.base_height = 900

        self.resize_ui()

        # Game objects
        self.game_map = None
        self.player = None
        self.weapon_drop = None
        self.projectiles = []

        self.weapon_delay = 5000
        self.last_weapon_removed_time = 0

    def resize_ui(self):
        scale = max(0.6, min(self.screen_height / 900, 1.5))

        self.title_font = pygame.font.SysFont("arial", int(56 * scale), bold=True)
        self.button_font = pygame.font.SysFont("arial", int(28 * scale))
        self.text_font = pygame.font.SysFont("arial", int(24 * scale))
        self.small_font = pygame.font.SysFont("arial", int(22 * scale))

        cx = self.screen_width // 2
        bw = int(self.screen_width * 0.25)
        bh = int(self.screen_height * 0.08)

        self.join_button = Button(cx - bw // 2, int(self.screen_height * 0.30), bw, bh, "Join Game")
        self.settings_button = Button(cx - bw // 2, int(self.screen_height * 0.42), bw, bh, "Settings")
        self.quit_button = Button(cx - bw // 2, int(self.screen_height * 0.54), bw, bh, "Quit")
        self.back_button = Button(cx - bw // 2, int(self.screen_height * 0.70), bw, bh, "Tilbage")

        sw = int(self.screen_width * 0.3)
        sx = cx - sw // 2

        self.music_slider = Slider(sx, int(self.screen_height * 0.40), sw, 0, 100, 50, "Music volume")
        self.sfx_slider = Slider(sx, int(self.screen_height * 0.53), sw, 0, 100, 50, "SFX volume")

    def start_game(self):
        self.game_map = GameMap(self.base_width, self.base_height)

        spawn = self.game_map.spawn_points[0]
        self.player = Player(spawn[0], spawn[1], 40, 60, (255, 255, 255))

        self.weapon_drop = None
        self.projectiles = []
        self.last_weapon_removed_time = pygame.time.get_ticks()

        self.state = "game"

    def spawn_weapon(self):
        self.weapon_drop = WeaponDrop(self.base_width)

    def remove_weapon(self):
        self.weapon_drop = None
        self.last_weapon_removed_time = pygame.time.get_ticks()

    def update_weapons(self):
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

    def shoot(self):
        if not self.player:
            return

        now = pygame.time.get_ticks()
        data = self.player.try_shoot(now)

        if data:
            self.projectiles.append(
                Projectile(data["x"], data["y"], self.player.direction, self.player.current_weapon)
            )

    def update_projectiles(self):
        remove = []

        for projectile in self.projectiles:
            projectile.update()

            if projectile.has_reached_max_range():
                remove.append(projectile)
                continue

            for plat in self.game_map.platforms:
                if projectile.rect.colliderect(plat):
                    remove.append(projectile)
                    break

        for projectile in remove:
            if projectile in self.projectiles:
                self.projectiles.remove(projectile)

    def update_game(self):
        keys = pygame.key.get_pressed()

        self.player.move(keys, self.game_map.platforms, self.base_width, self.base_height)
        self.player.update_reload(pygame.time.get_ticks())

        self.update_weapons()
        self.update_projectiles()

    def draw_game(self):
        surface = pygame.Surface((self.base_width, self.base_height))

        self.game_map.draw(surface)
        self.player.draw(surface)

        if self.weapon_drop:
            self.weapon_drop.draw(surface)

        for projectile in self.projectiles:
            projectile.draw(surface)

        scaled = pygame.transform.scale(surface, (self.screen_width, self.screen_height))
        self.screen.blit(scaled, (0, 0))

        self.draw_game_info()

    def draw_game_info(self):
        hp_text = self.small_font.render(
            f"HP: {self.player.hitpoints}   Lives: {self.player.lives}",
            True, (0, 0, 0)
        )
        self.screen.blit(hp_text, (20, 20))

        if self.player.current_weapon is None:
            weapon_text = self.small_font.render("Weapon: None   Ammo: 0", True, (0, 0, 0))
        else:
            weapon_text = self.small_font.render(
                f"Weapon: {self.player.current_weapon.name}   Ammo: {self.player.ammo}",
                True, (0, 0, 0)
            )

        self.screen.blit(weapon_text, (20, 50))

    def draw_menu(self):
        self.screen.fill((25, 25, 25))

        title = self.title_font.render("Menu", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, int(self.screen_height * 0.18)))
        self.screen.blit(title, title_rect)

        self.join_button.draw(self.screen, self.button_font)
        self.settings_button.draw(self.screen, self.button_font)
        self.quit_button.draw(self.screen, self.button_font)

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
                self.state = "menu"

            if event.key == pygame.K_r:
                self.player.start_reload(pygame.time.get_ticks())

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.shoot()

    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.VIDEORESIZE:
                    self.screen_width, self.screen_height = event.w, event.h
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.resize_ui()

                if self.state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.join_button.is_clicked(event.pos):
                            self.start_game()
                        elif self.settings_button.is_clicked(event.pos):
                            self.state = "settings"
                        elif self.quit_button.is_clicked(event.pos):
                            self.running = False

                elif self.state == "settings":
                    self.music_slider.handle_event(event)

                    self.sfx_slider.handle_event(event)

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.back_button.is_clicked(event.pos):
                            self.state = "menu"

                elif self.state == "game":
                    self.handle_game_events(event)

            if self.state == "game":
                self.update_game()

            if self.state == "menu":
                self.draw_menu()
            elif self.state == "settings":
                self.draw_settings()
            elif self.state == "game":
                self.draw_game()

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    GameApp().run()