import pygame
import sys
import ball

pygame.init()

WIDTH = 600
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")

clock = pygame.time.Clock()

move_delay = 100  # milliseconds between moves while key is held
last_move_time = 0  # tracks when we last moved

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:  
            if event.key == pygame.K_UP:
                ball.press_up()
            if event.key == pygame.K_DOWN:
                ball.press_down(HEIGHT)
            if event.key == pygame.K_LEFT:
                ball.press_left()
            if event.key == pygame.K_RIGHT:
                ball.press_right(WIDTH)
            last_move_time = pygame.time.get_ticks()  # when last move happened

    # when key is hold
    now = pygame.time.get_ticks()  # current time 
    if now - last_move_time >= move_delay:
        keys = pygame.key.get_pressed()  # check which keys are currently down
        moved = False

        if keys[pygame.K_UP]:
            ball.press_up()
            moved = True
        if keys[pygame.K_DOWN]:
            ball.press_down(HEIGHT)
            moved = True
        if keys[pygame.K_LEFT]:
            ball.press_left()
            moved = True
        if keys[pygame.K_RIGHT]:
            ball.press_right(WIDTH)
            moved = True

        if moved:
            last_move_time = now  # reset timer

    ball.update()  # movement

    screen.fill((255, 255, 255))
    pygame.draw.circle(screen, (255, 0, 0), (int(ball.x), int(ball.y)), ball.radius)

    pygame.display.flip()
    clock.tick(60) 
