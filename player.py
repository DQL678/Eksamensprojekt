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

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self, keys, platforms, screen_width, screen_height):
        move_x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x = -self.vel

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x = self.vel

        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.y_velocity = -self.jump_strength
            self.on_ground = False

        self.move_horizontal(move_x, screen_width)

        self.y_velocity += self.gravity
        if self.y_velocity > 16:
            self.y_velocity = 16

        self.move_vertical(platforms)

        self.x = self.rect.x
        self.y = self.rect.y

    def move_horizontal(self, dx, screen_width):
        self.rect.x += dx

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > screen_width:
            self.rect.right = screen_width

    def move_vertical(self, platforms):
        self.on_ground = False

        old_bottom = self.rect.bottom
        self.rect.y += int(self.y_velocity)

        for platform in platforms:
            if self.y_velocity >= 0:
                landed_on_platform = (
                    self.rect.colliderect(platform)
                    and old_bottom <= platform.top + 10
                )

                if landed_on_platform:
                    self.rect.bottom = platform.top
                    self.y_velocity = 0
                    self.on_ground = True

    def shoot(self):
        pass