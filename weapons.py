import pygame
import random


class WeaponDrop:
    def __init__(self, screen_width):
        self.width = 30
        self.height = 20

        self.x = random.randint(50, screen_width - 50)
        self.y = -40

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.color = (200, 50, 50)

        self.y_velocity = 0
        self.gravity = 0.5
        self.max_fall_speed = 12

        self.on_ground = False
        self.name = "Basic Gun"

    def update(self, floor):
        if not self.on_ground:
            self.y_velocity += self.gravity

            if self.y_velocity > self.max_fall_speed:
                self.y_velocity = self.max_fall_speed

            self.rect.y += int(self.y_velocity)

            if self.rect.colliderect(floor):
                self.rect.bottom = floor.top
                self.y_velocity = 0
                self.on_ground = True

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def is_picked_up(self, player):
        return self.rect.colliderect(player.rect)