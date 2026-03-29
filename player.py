import pygame

class Player:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.rect = (x,y,width,height)
        self.vel = 3

    def draw(self):
        pygame.draw.rect(win, self.color, self.rect)

    def move(self):
        keys = pygame.keys.get.pressed()

        if keys[pygame.K_LEFT]:

        if keys[pygame.K_RIGHT]:

        if keys[pygame.K_UP]:

        if keys[pygame.K_DOWN]:
