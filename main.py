import pygame
from player import Player

width = 500
height = 500
win = pygame.display.set_mode((width, height))
pygame.display.set_caption('Client')

client = 0

def redrawWindow():
    win.fill((0, 0, 0))
    pygame.display.update()

def main():
    run = True
    p = Player(50, 50, 100, 100, (255, 255, 255))
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        p.move()
        redrawWindow(win, p)

main()