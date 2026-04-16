import pygame
import sys
from clock import MickeysClock


def main():
    pygame.init()

    SCREEN_W, SCREEN_H = 800, 800
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Mickey's Clock")

    clock_obj  = MickeysClock(SCREEN_W, SCREEN_H)
    clock_obj.load_images()

    fps_clock  = pygame.time.Clock()
    BG_COLOR   = (10, 10, 10)          #background

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        screen.fill(BG_COLOR)
        clock_obj.draw(screen)
        pygame.display.flip()
        fps_clock.tick(1)   #frames per second


if __name__ == "__main__":
    main()
