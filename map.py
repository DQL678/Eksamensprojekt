import pygame


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.platforms = []

        self.create_platforms()
        self.floor = self.platforms[0]

    def create_platforms(self):
        self.platforms = [
            # Gulv
            pygame.Rect(0, 860, 1500, 40),

            # 1. række (3 platforme)
            pygame.Rect(180, 100, 140, 8),
            pygame.Rect(680, 100, 140, 8),
            pygame.Rect(1180, 100, 140, 8),

            # 2. række (4 platforme)
            pygame.Rect(60, 220, 120, 8),
            pygame.Rect(400, 220, 160, 8),
            pygame.Rect(940, 220, 160, 8),
            pygame.Rect(1280, 220, 120, 8),

            # 3. række (3 platforme)
            pygame.Rect(140, 340, 140, 8),
            pygame.Rect(680, 340, 140, 8),
            pygame.Rect(1220, 340, 140, 8),

            # 4. række (4 platforme)
            pygame.Rect(40, 460, 120, 8),
            pygame.Rect(370, 460, 160, 8),
            pygame.Rect(970, 460, 160, 8),
            pygame.Rect(1300, 460, 120, 8),

            # 5. række (3 platforme)
            pygame.Rect(180, 580, 140, 8),
            pygame.Rect(680, 580, 140, 8),
            pygame.Rect(1180, 580, 140, 8),

            # 6. række (4 platforme)
            pygame.Rect(60, 700, 120, 8),
            pygame.Rect(400, 700, 160, 8),
            pygame.Rect(940, 700, 160, 8),
            pygame.Rect(1280, 700, 120, 8),

            # 7. række (3 platforme)
            pygame.Rect(180, 800, 140, 8),
            pygame.Rect(680, 800, 140, 8),
            pygame.Rect(1180, 800, 140, 8),
        ]

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

    screen_width = 1500
    screen_height = 900
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Map Preview")

    clock = pygame.time.Clock()
    game_map = GameMap(screen_width, screen_height)

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game_map.draw(screen)
        pygame.display.update()

    pygame.quit()