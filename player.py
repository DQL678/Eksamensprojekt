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
        self.score = 0

        self.frozen_until = 0
        self.slowed_until = 0
        self.slow_amount = 0

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

        if self.current_weapon is not None:
            if self.current_weapon.image is not None:
                weapon_width, weapon_height = self.current_weapon.image_size
                weapon_image = pygame.transform.scale(
                    self.current_weapon.image,
                    (weapon_width, weapon_height)
                )

                if self.direction == -1:
                    weapon_image = pygame.transform.flip(weapon_image, True, False)
                    weapon_x = self.rect.left - weapon_width + 10
                else:
                    weapon_x = self.rect.right - 10

                weapon_y = self.rect.centery - weapon_height // 2
                win.blit(weapon_image, (weapon_x, weapon_y))

    def is_frozen(self, current_time):
        return current_time < self.frozen_until

    def is_slowed(self, current_time):
        return current_time < self.slowed_until

    def freeze(self, duration_ms, current_time):
        self.frozen_until = max(self.frozen_until, current_time + duration_ms)

    def apply_slow(self, duration_ms, amount, current_time):
        self.slowed_until = max(self.slowed_until, current_time + duration_ms)
        self.slow_amount = amount

    def move(self, keys, platforms, screen_width, screen_height):
        current_time = pygame.time.get_ticks()
        move_x = 0
        current_speed = self.vel

        if self.is_slowed(current_time):
            current_speed = self.vel * (1 - self.slow_amount)

        if not self.is_frozen(current_time):
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move_x = -current_speed
                self.direction = -1

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move_x = current_speed
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
        self.rect.x += int(dx)

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

    def take_projectile_hit(self, projectile, current_time):
        self.hitpoints -= projectile.damage

        if projectile.special_type == "freeze":
            self.freeze(projectile.special_duration, current_time)

        if projectile.special_type == "slow":
            self.apply_slow(
                projectile.special_duration,
                projectile.special_amount,
                current_time
            )