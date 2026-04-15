import pygame
import random
import json
import os


def load_weapon_data():
    folder = os.path.dirname(__file__)

    possible_filenames = [
        "Weapons_Data.json",
        "Weapons_Data"
    ]

    for filename in possible_filenames:
        filepath = os.path.join(folder, filename)

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)["weapons"]

    raise FileNotFoundError(
        "Could not find Weapons_Data.json or Weapons_Data in the same folder as weapons.py"
    )


weapon_data_list = load_weapon_data()


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


# Hjælpefunktion til JSON-filen om Weapons_Data
def create_weapon_from_json(name):
    for weapon in weapon_data_list:
        if weapon["name"] == name:
            projectile = weapon["projectile"]

            return Weapon(
                name=weapon["name"],
                fire_rate=weapon["fire_rate"],
                projectile_speed=projectile["speed"],
                projectile_size=projectile["size"],
                projectile_range=projectile["range"],
                projectile_count=projectile["count"],
                projectile_damage=projectile["damage"],
                reload_speed=weapon["reload_speed"],
                ammo_capacity=weapon["ammo_capacity"]
            )

    raise ValueError(f"Våbnet '{name}' blev ikke fundet i JSON-filen.")


def create_handgun():
    return create_weapon_from_json("Handgun")


def create_sniper():
    return create_weapon_from_json("Sniper")


def create_shotgun():
    return create_weapon_from_json("Shotgun")


def create_assault_rifle():
    return create_weapon_from_json("Assault Rifle")


class WeaponDrop:
    def __init__(self, screen_width):
        self.width = 30
        self.height = 20

        self.x = random.randint(50, screen_width - 50)
        self.y = -40
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.weapon = random.choice([
            create_handgun(),
            create_sniper(),
            create_shotgun(),
            create_assault_rifle()
        ])

        if self.weapon.name == "Handgun":
            self.color = (200, 50, 50)   # rød
        elif self.weapon.name == "Sniper":
            self.color = (50, 80, 200)   # blå
        elif self.weapon.name == "Shotgun":
            self.color = (210, 140, 40)  # orange
        else:
            self.color = (50, 170, 90)   # grøn

        self.y_velocity = 0
        self.gravity = 0.3
        self.max_fall_speed = 6

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
    def __init__(self, x, y, direction, weapon, spread=0):
        self.size = weapon.projectile_size
        self.rect = pygame.Rect(x, y, self.size, self.size)

        self.direction = direction
        self.speed = weapon.projectile_speed
        self.damage = weapon.projectile_damage
        self.max_distance = weapon.projectile_range

        self.distance_travelled = 0
        self.y_speed = spread

        if weapon.name == "Sniper":
            self.color = (40, 40, 180)
        elif weapon.name == "Shotgun":
            self.color = (180, 120, 20)
        elif weapon.name == "Assault Rifle":
            self.color = (40, 150, 70)
        else:
            self.color = (200, 0, 0)

    def update(self):
        move_x = self.speed * self.direction
        self.rect.x += move_x
        self.rect.y += self.y_speed

        self.distance_travelled += abs(move_x)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def has_reached_max_range(self):
        return self.distance_travelled >= self.max_distance