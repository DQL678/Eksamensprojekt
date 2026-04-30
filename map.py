import pygame
import random


class GameMap:
    def __init__(self, width, height, map_number=1):
        self.width = width
        self.height = height
        self.map_number = map_number
        self.platforms = []
        self.spawn_points = []

        self.create_platforms()
        self.floor = self.platforms[0]
        self.create_spawn_points()

    def create_platforms(self):
        if self.map_number == 1:
            self.create_map_1()
        elif self.map_number == 2:
            self.create_map_2()

    def create_map_1(self):
        self.platforms = [
            pygame.Rect(0, 860, 1600, 40),

            pygame.Rect(180, 100, 140, 8),
            pygame.Rect(700, 100, 200, 8),
            pygame.Rect(1280, 100, 140, 8),

            pygame.Rect(60, 220, 120, 8),
            pygame.Rect(420, 220, 160, 8),
            pygame.Rect(1020, 220, 160, 8),
            pygame.Rect(1380, 220, 120, 8),

            pygame.Rect(140, 340, 140, 8),
            pygame.Rect(700, 340, 200, 8),
            pygame.Rect(1320, 340, 140, 8),

            pygame.Rect(40, 460, 120, 8),
            pygame.Rect(390, 460, 160, 8),
            pygame.Rect(1050, 460, 160, 8),
            pygame.Rect(1400, 460, 120, 8),

            pygame.Rect(180, 580, 140, 8),
            pygame.Rect(700, 580, 200, 8),
            pygame.Rect(1280, 580, 140, 8),

            pygame.Rect(60, 700, 120, 8),
            pygame.Rect(420, 700, 160, 8),
            pygame.Rect(1020, 700, 160, 8),
            pygame.Rect(1380, 700, 120, 8),

            pygame.Rect(180, 820, 140, 8),
            pygame.Rect(700, 820, 200, 8),
            pygame.Rect(1280, 820, 140, 8),
        ]

    def create_map_2(self):
        self.platforms = [
            pygame.Rect(0, 860, 1600, 40),

            pygame.Rect(650, 130, 300, 8),

            pygame.Rect(520, 250, 180, 8),
            pygame.Rect(900, 250, 180, 8),

            pygame.Rect(390, 370, 180, 8),
            pygame.Rect(1030, 370, 180, 8),

            pygame.Rect(260, 490, 180, 8),
            pygame.Rect(1160, 490, 180, 8),

            pygame.Rect(390, 610, 180, 8),
            pygame.Rect(1030, 610, 180, 8),

            pygame.Rect(520, 730, 180, 8),
            pygame.Rect(900, 730, 180, 8),

            pygame.Rect(650, 820, 300, 8),
        ]

    def create_spawn_points(self):
        self.spawn_points = [
            (100, self.floor.top - 60),
            (760, self.floor.top - 60),
            (1400, self.floor.top - 60),
        ]

    def get_random_spawn_point(self):
        return random.choice(self.spawn_points)

    def draw_background(self, screen):
        screen.fill((215, 215, 215))

    def draw_platforms(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, (0, 0, 0), platform)

    def draw(self, screen):
        self.draw_background(screen)
        self.draw_platforms(screen)


if __name__ == "__main__":
    pygame.init()

    screen_width = 1600
    screen_height = 900
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Map Preview")

    clock = pygame.time.Clock()
    game_map = GameMap(screen_width, screen_height, 1)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game_map.draw(screen)
        pygame.display.update()

    pygame.quit()