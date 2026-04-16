import pygame
import sys
import player  

pygame.init()

screen = pygame.display.set_mode((500, 300))
pygame.display.set_caption("Music Player")

font = pygame.font.SysFont("monospace", 20)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                player.play()

            if event.key == pygame.K_s:
                player.stop()

            if event.key == pygame.K_n:
                player.next_track()

            if event.key == pygame.K_b:
                player.prev_track()

            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    screen.fill((30, 30, 30))  # background

    # show current track name and number
    track_name = player.tracks[player.current]  # get file path of current track
    name_text = font.render("Track: " + track_name, True, (255, 255, 255))
    screen.blit(name_text, (20, 40))

    # show track number
    num_text = font.render("Track " + str(player.current + 1) + " of " + str(len(player.tracks)), True, (180, 180, 180))
    screen.blit(num_text, (20, 80))

    # show how many seconds have played
    pos = player.get_position()
    pos_text = font.render("Position: " + str(pos) + "s", True, (180, 180, 180))
    screen.blit(pos_text, (20, 120))

    # show if playing or stopped
    if player.is_playing:
        status_text = font.render("Status: Playing", True, (100, 220, 100))
    else:
        status_text = font.render("Status: Stopped", True, (220, 100, 100))
    screen.blit(status_text, (20, 160))

    # show controls at the bottom
    controls = font.render("P=Play  S=Stop  N=Next  B=Back  Q=Quit", True, (120, 120, 120))
    screen.blit(controls, (20, 240))

    pygame.display.flip()
    clock.tick(30)  # update 30 times per second
