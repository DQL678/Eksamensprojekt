import pygame


class Player:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

        self.rect = pygame.Rect(x, y, width, height)

        self.vel = 5
        self.jump_strength = 15
        self.gravity = 0.7
        self.y_velocity = 0
        self.on_ground = False

        self.direction = 1

        self.current_weapon = None
        self.ammo = 0
        self.is_reloading = False
        self.reload_start_time = 0
        self.last_shot_time = 0

        self.max_hitpoints = 100
        self.hitpoints = 100
        self.lives = 3

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self, keys, platforms, screen_width, screen_height):
        move_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x = -self.vel
            self.direction = -1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x = self.vel
            self.direction = 1

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.y_velocity = -self.jump_strength
            self.on_ground = False

        self.move_horizontal(move_x, platforms, screen_width)

        self.y_velocity += self.gravity
        if self.y_velocity > 16:
            self.y_velocity = 16

        self.move_vertical(platforms, screen_height)

        self.x = self.rect.x
        self.y = self.rect.y

    def move_horizontal(self, dx, platforms, screen_width):
        self.rect.x += dx

        for platform in platforms:
            if self.rect.colliderect(platform):
                if dx > 0:
                    self.rect.right = platform.left
                elif dx < 0:
                    self.rect.left = platform.right

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def move_vertical(self, platforms, screen_height):
        self.on_ground = False
        self.rect.y += int(self.y_velocity)

        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.y_velocity > 0:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_ground = True
                elif self.y_velocity < 0:
                    self.rect.top = platform.bottom
                    self.y_velocity = 0

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.y_velocity = 0
            self.on_ground = True

    def pick_up_weapon(self, weapon_drop):
        self.current_weapon = weapon_drop.weapon
        self.ammo = self.current_weapon.ammo_capacity
        self.is_reloading = False

    def can_shoot(self, current_time):
        if self.current_weapon is None:
            return False
        if self.is_reloading:
            return False
        if self.ammo <= 0:
            return False

        return current_time - self.last_shot_time >= self.current_weapon.fire_rate

    def try_shoot(self, current_time):
        if not self.can_shoot(current_time):
            return []

        self.last_shot_time = current_time
        self.ammo -= 1

        projectile_positions = []
        count = self.current_weapon.projectile_count

        center_x = self.rect.centerx
        center_y = self.rect.centery

        if count == 1:
            projectile_positions.append({
                "x": center_x,
                "y": center_y
            })
        else:
            spacing = 10
            start_y = center_y - ((count - 1) * spacing) // 2

            for i in range(count):
                projectile_positions.append({
                    "x": center_x,
                    "y": start_y + i * spacing
                })

        return projectile_positions

    def start_reload(self, current_time):
        if self.current_weapon is None:
            return
        if self.is_reloading:
            return
        if self.ammo == self.current_weapon.ammo_capacity:
            return

        self.is_reloading = True
        self.reload_start_time = current_time

    def update_reload(self, current_time):
        if self.current_weapon is None:
            return

        if self.is_reloading:
            if current_time - self.reload_start_time >= self.current_weapon.reload_speed:
                self.ammo = self.current_weapon.ammo_capacity
                self.is_reloading = False