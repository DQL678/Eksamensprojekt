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

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


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
            if handle_rect.collidepoint(event.pos) or self.bar_rect.inflate(0, 20).collidepoint(event.pos):
                self.dragging = True
                self.update_value(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_value(event.pos[0])

    def update_value(self, mouse_x):
        if mouse_x < self.x:
            mouse_x = self.x
        if mouse_x > self.x + self.width:
            mouse_x = self.x + self.width

        percent = (mouse_x - self.x) / self.width
        self.value = int(self.min_value + percent * (self.max_value - self.min_value))

    def draw(self, screen, font):
        text_surface = font.render(f"{self.label}: {self.value}", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y - 35))
        screen.blit(text_surface, text_rect)

        pygame.draw.rect(screen, (170, 170, 170), self.bar_rect)
        handle_x = self.get_handle_x()
        pygame.draw.circle(screen, (240, 240, 240), (handle_x, self.y + 3), self.handle_radius)


class GameApp:
    def __init__(self):
        pygame.init()

        self.screen_width = 1600
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Multiplayer Game")

        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        self.title_font = pygame.font.SysFont("arial", 56, bold=True)
        self.button_font = pygame.font.SysFont("arial", 28)
        self.text_font = pygame.font.SysFont("arial", 30)
        self.small_font = pygame.font.SysFont("arial", 22)

        center_x = self.screen_width // 2
        button_width = 320
        button_height = 70

        self.join_button = Button(center_x - button_width // 2, 300, button_width, button_height, "Join Game")
        self.settings_button = Button(center_x - button_width // 2, 400, button_width, button_height, "Settings")
        self.quit_button = Button(center_x - button_width // 2, 500, button_width, button_height, "Quit")
        self.back_button = Button(center_x - button_width // 2, 620, button_width, button_height, "Tilbage")

        slider_width = 420
        slider_x = center_x - slider_width // 2
        self.music_slider = Slider(slider_x, 320, slider_width, 0, 100, 50, "Music volume")
        self.sfx_slider = Slider(slider_x, 430, slider_width, 0, 100, 50, "SFX volume")

        self.game_map = None
        self.player = None
        self.weapon_drop = None
        self.projectiles = []

        self.weapon_delay = 5000
        self.last_weapon_removed_time = 0

    def start_game(self):
        self.game_map = GameMap(self.screen_width, self.screen_height)

        spawn = self.game_map.spawn_points[0]
        self.player = Player(spawn[0], spawn[1], 40, 60, (255, 255, 255))

        self.weapon_drop = None
        self.projectiles = []
        self.last_weapon_removed_time = pygame.time.get_ticks()

        self.state = "game"

    def spawn_new_weapon(self):
        self.weapon_drop = WeaponDrop(self.screen_width)

    def remove_weapon_and_start_delay(self):
        self.weapon_drop = None
        self.last_weapon_removed_time = pygame.time.get_ticks()

    def draw_menu(self):
        self.screen.fill((25, 25, 25))
        title = self.title_font.render("Menu", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(title, title_rect)

        self.join_button.draw(self.screen, self.button_font)
        self.settings_button.draw(self.screen, self.button_font)
        self.quit_button.draw(self.screen, self.button_font)

    def draw_settings(self):
        self.screen.fill((35, 35, 50))
        title = self.title_font.render("Settings", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 180))
        self.screen.blit(title, title_rect)

        self.music_slider.draw(self.screen, self.text_font)
        self.sfx_slider.draw(self.screen, self.text_font)
        self.back_button.draw(self.screen, self.button_font)

    def draw_game_info(self):
        hp_text = self.small_font.render(
            f"HP: {self.player.hitpoints}   Lives: {self.player.lives}",
            True, (0, 0, 0)
        )

        if self.player.current_weapon is None:
            weapon_text = self.small_font.render("Weapon: None   Ammo: 0", True, (0, 0, 0))
        else:
            weapon_text = self.small_font.render(
                f"Weapon: {self.player.current_weapon.name}   Ammo: {self.player.ammo}",
                True, (0, 0, 0)
            )

        self.screen.blit(hp_text, (20, 20))
        self.screen.blit(weapon_text, (20, 50))

    def draw_game(self):
        self.game_map.draw(self.screen)
        self.player.draw(self.screen)

        if self.weapon_drop is not None:
            self.weapon_drop.draw(self.screen)

        for projectile in self.projectiles:
            projectile.draw(self.screen)

        self.draw_game_info()

    def handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.join_button.is_clicked(event.pos):
                self.start_game()
            elif self.settings_button.is_clicked(event.pos):
                self.state = "settings"
            elif self.quit_button.is_clicked(event.pos):
                self.running = False

    def handle_settings_events(self, event):
        self.music_slider.handle_event(event)
        self.sfx_slider.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.is_clicked(event.pos):
                self.state = "menu"

    def create_projectile(self):
        if self.player is None:
            return

        current_time = pygame.time.get_ticks()
        projectile_data = self.player.try_shoot(current_time)

        if projectile_data is not None:
            projectile = Projectile(
                projectile_data["x"],
                projectile_data["y"],
                self.player.direction,
                self.player.current_weapon
            )
            self.projectiles.append(projectile)

    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "menu"

            if event.key == pygame.K_r:
                self.player.start_reload(pygame.time.get_ticks())

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.create_projectile()

    def update_weapon_system(self):
        current_time = pygame.time.get_ticks()

        if self.weapon_drop is None:
            if current_time - self.last_weapon_removed_time >= self.weapon_delay:
                self.spawn_new_weapon()
        else:
            self.weapon_drop.update()

            if self.weapon_drop.is_picked_up(self.player):
                self.player.pick_up_weapon(self.weapon_drop)
                self.remove_weapon_and_start_delay()

            elif self.weapon_drop.is_out_of_map(self.screen_height):
                self.remove_weapon_and_start_delay()

    def update_projectiles(self):
        projectiles_to_remove = []

        for projectile in self.projectiles:
            projectile.update()

            if projectile.has_reached_max_range():
                projectiles_to_remove.append(projectile)
                continue

            for platform in self.game_map.platforms:
                if projectile.rect.colliderect(platform):
                    projectiles_to_remove.append(projectile)
                    break

        for projectile in projectiles_to_remove:
            if projectile in self.projectiles:
                self.projectiles.remove(projectile)

    def update_game(self):
        keys = pygame.key.get_pressed()

        self.player.move(keys, self.game_map.platforms, self.screen_width, self.screen_height)
        self.player.update_reload(pygame.time.get_ticks())

        self.update_weapon_system()
        self.update_projectiles()

    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if self.state == "menu":
                    self.handle_menu_events(event)
                elif self.state == "settings":
                    self.handle_settings_events(event)
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
    app = GameApp()
    app.run()