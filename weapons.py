import pygame
import random


class Weapon:
    def __init__(
        self,
        name,
        fire_rate,
        projectile_speed,
        projectile_size,
        projectile_range,
        projectile_count,
        projectile_damage,
        reload_speed,
        ammo_capacity
    ):
        self.name = name
        self.fire_rate = fire_rate
        self.projectile_speed = projectile_speed
        self.projectile_size = projectile_size
        self.projectile_range = projectile_range
        self.projectile_count = projectile_count
        self.projectile_damage = projectile_damage
        self.reload_speed = reload_speed
        self.ammo_capacity = ammo_capacity


def create_handgun():
    return Weapon(
        name="Handgun",
        fire_rate=300,
        projectile_speed=12,
        projectile_size=8,
        projectile_range=500,
        projectile_count=1,
        projectile_damage=20,
        reload_speed=1200,
        ammo_capacity=12
    )


class WeaponDrop:
    def __init__(self, screen_width):
        self.width = 30
        self.height = 20

        self.x = random.randint(50, screen_width - 50)
        self.y = -40

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.color = (200, 50, 50)
        self.weapon = create_handgun()

        self.y_velocity = 0
        self.gravity = 0.5
        self.max_fall_speed = 12

    def update(self):
        self.y_velocity += self.gravity

        if self.y_velocity > self.max_fall_speed:
            self.y_velocity = self.max_fall_speed

        self.rect.y += int(self.y_velocity)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def is_picked_up(self, player):
        return self.rect.colliderect(player.rect)

    def is_out_of_map(self, screen_height):
        return self.rect.top > screen_height


class Projectile:
    def __init__(self, x, y, direction, weapon):
        self.size = weapon.projectile_size
        self.rect = pygame.Rect(x, y, self.size, self.size)

        self.direction = direction
        self.speed = weapon.projectile_speed
        self.damage = weapon.projectile_damage
        self.max_distance = weapon.projectile_range

        self.distance_travelled = 0
        self.color = (200, 0, 0)

    def update(self):
        move_x = self.speed * self.direction
        self.rect.x += move_x
        self.distance_travelled += abs(move_x)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def has_reached_max_range(self):
        return self.distance_travelled >= self.max_distance