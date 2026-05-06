import pygame
import random
import json
import os


def load_weapon_data():
    folder = os.path.dirname(__file__)

    possible_filenames = ["Weapons_Data.json", "Weapons_Data"]

    for filename in possible_filenames:
        filepath = os.path.join(folder, filename)

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as file:
                return json.load(file)["weapons"]

    raise FileNotFoundError("Could not find Weapons_Data.json or Weapons_Data in the same folder as weapons.py")


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
        ammo_capacity,
        special_type=None,
        special_duration=0,
        special_amount=0,
        image=None,
        image_size=None
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

        self.special_type = special_type
        self.special_duration = special_duration
        self.special_amount = special_amount

        self.image = image
        self.image_size = image_size


BASE_DIR = os.path.dirname(__file__)
WEAPON_FOLDER = os.path.join(BASE_DIR, "Weapons")
WEAPON_IMAGES = {}


def load_weapon_images():
    global WEAPON_IMAGES

    def load_safe(filename):
        path = os.path.join(WEAPON_FOLDER, filename)

        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()

        print("Missing weapon image:", filename)
        return None

    WEAPON_IMAGES = {
        "Handgun": load_safe("Handgun.png"),
        "Sniper": load_safe("Sniper.png"),
        "Shotgun": load_safe("Shotgun.png"),
        "Assault Rifle": load_safe("Assault_Rifle.png"),
        "Minigun": load_safe("Minigun.png"),
        "Freeze Gun": load_safe("Freeze_Gun.png"),
        "Laserbeamer": load_safe("Laserbeamer.png"),
        "Snowball Cannon": load_safe("Snowball_Cannon.png")
    }


def create_weapon_from_json(name):
    for weapon in weapon_data_list:
        if weapon["name"] == name:
            projectile = weapon["projectile"]

            special = weapon.get("special", {})
            special_type = special.get("type")
            special_duration = special.get("duration", 0)
            special_amount = special.get("amount", 0)

            image = WEAPON_IMAGES.get(weapon["name"])

            image_sizes = {
                "Handgun": (60, 50),
                "Sniper": (120, 30),
                "Shotgun": (100, 25),
                "Assault Rifle": (130, 55),
                "Minigun": (100, 40),
                "Freeze Gun": (80, 45),
                "Laserbeamer": (110, 40),
                "Snowball Cannon": (100, 50)
            }

            size = image_sizes.get(weapon["name"], (50, 30))

            return Weapon(
                name=weapon["name"],
                fire_rate=weapon["fire_rate"],
                projectile_speed=projectile["speed"],
                projectile_size=projectile["size"],
                projectile_range=projectile["range"],
                projectile_count=projectile["count"],
                projectile_damage=projectile["damage"],
                reload_speed=weapon["reload_speed"],
                ammo_capacity=weapon["ammo_capacity"],
                special_type=special_type,
                special_duration=special_duration,
                special_amount=special_amount,
                image=image,
                image_size=size
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


def create_minigun():
    return create_weapon_from_json("Minigun")


def create_freeze_gun():
    return create_weapon_from_json("Freeze Gun")


def create_laserbeamer():
    return create_weapon_from_json("Laserbeamer")


def create_snowball_cannon():
    return create_weapon_from_json("Snowball Cannon")


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
            create_assault_rifle(),
            create_minigun(),
            create_freeze_gun(),
            create_laserbeamer(),
            create_snowball_cannon()
        ])

        self.y_velocity = 0
        self.gravity = 0.18
        self.max_fall_speed = 4

    def update(self):
        self.y_velocity += self.gravity

        if self.y_velocity > self.max_fall_speed:
            self.y_velocity = self.max_fall_speed

        self.rect.y += int(self.y_velocity)

    def draw(self, screen):
        if self.weapon.image:
            width, height = self.weapon.image_size
            image = pygame.transform.scale(self.weapon.image, (width, height))
            image_rect = image.get_rect(center=self.rect.center)
            screen.blit(image, image_rect)
        else:
            pygame.draw.rect(screen, (0, 0, 0), self.rect)

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

        self.special_type = weapon.special_type
        self.special_duration = weapon.special_duration
        self.special_amount = weapon.special_amount

        self.is_laser = False

        if weapon.name == "Sniper":
            self.color = (40, 40, 180)
        elif weapon.name == "Shotgun":
            self.color = (180, 120, 20)
        elif weapon.name == "Assault Rifle":
            self.color = (40, 150, 70)
        elif weapon.name == "Minigun":
            self.color = (130, 40, 150)
        elif weapon.name == "Freeze Gun":
            self.color = (80, 220, 255)
        elif weapon.name == "Snowball Cannon":
            self.color = (180, 240, 255)
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


class LaserBeam:
    def __init__(self, x, y, direction, weapon, platforms, screen_width):
        self.x = x
        self.y = y
        self.direction = direction
        self.damage = weapon.projectile_damage
        self.size = weapon.projectile_size

        self.special_type = weapon.special_type
        self.special_duration = weapon.special_duration
        self.special_amount = weapon.special_amount

        self.is_laser = True

        self.created_time = pygame.time.get_ticks()
        self.duration = weapon.special_duration

        self.start_pos = (x, y)
        self.end_pos = self.find_end_position(platforms, screen_width)

        left = min(self.start_pos[0], self.end_pos[0])
        width = abs(self.end_pos[0] - self.start_pos[0])
        self.rect = pygame.Rect(left, y - self.size // 2, width, self.size)

        self.color = (255, 0, 0)

    def find_end_position(self, platforms, screen_width):
        end_x = screen_width if self.direction == 1 else 0

        laser_top = self.y - self.size // 2
        laser_bottom = self.y + self.size // 2

        closest_distance = screen_width

        for platform in platforms:
            laser_hits_platform_height = (laser_bottom >= platform.top and laser_top <= platform.bottom)

            if laser_hits_platform_height:
                if self.direction == 1 and platform.left > self.x:
                    distance = platform.left - self.x

                    if distance < closest_distance:
                        closest_distance = distance
                        end_x = platform.left

                elif self.direction == -1 and platform.right < self.x:
                    distance = self.x - platform.right

                    if distance < closest_distance:
                        closest_distance = distance
                        end_x = platform.right

        return (end_x, self.y)

    def update(self):
        pass

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.start_pos, self.end_pos, self.size)

    def has_reached_max_range(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.created_time > self.duration