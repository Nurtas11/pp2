import pygame, sys, random, time, os
from racer import Player, Enemy, Coin, Hazard, PowerUp
from persistence import load_settings, save_settings, save_score, load_leaderboard
from ui import UI

# mixer settings for better sound performance
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init() 

# window size and title
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Arcade Edition")

# timing variables
FPS = 60
FramePerSec = pygame.time.Clock()
ui = UI(DISPLAYSURF)

ASSET_PATH = "assets"

# load saved user preferences
settings = load_settings()
username = ""
game_state = "NAME_INPUT"
final_score_display = 0 

# road background
bg_path = os.path.join(ASSET_PATH, "AnimatedStreet.png")
background_img = pygame.image.load(bg_path)

# setup music files
music_path = os.path.join(ASSET_PATH, "background.mp3")
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)

# load the crash sfx
crash_path = os.path.join(ASSET_PATH, "crash.mp3")
crash_sound = None
if os.path.exists(crash_path):
    crash_sound = pygame.mixer.Sound(crash_path)
    crash_sound.set_volume(0.8)

def play_crash_sound():
    # helper to check settings before making noise
    if settings["sound"] and crash_sound:
        crash_sound.play()

def update_music():
    # start or stop music depending on settings toggle
    if settings["sound"]:
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.stop()

update_music()

def reset_game():
    # clear everything and start fresh for a new run
    global player, enemies, coins, hazards, powerups, all_sprites
    global score, coin_score, distance, speed
    
    player = Player(settings["car_color"])
    # initial difficulty speed
    speed = 5 if settings["difficulty"] == "Easy" else 7
    score = 0
    coin_score = 0
    distance = 0
    
    # setup sprite groups for collision detection
    enemies = pygame.sprite.Group([Enemy(speed)])
    coins = pygame.sprite.Group([Coin()])
    hazards = pygame.sprite.Group([Hazard("Oil"), Hazard("Pothole")])
    powerups = pygame.sprite.Group([PowerUp("Shield"), PowerUp("Nitro"), PowerUp("Repair")])
    
    # one group to rule them all for drawing
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    for g in [enemies, coins, hazards, powerups]: 
        all_sprites.add(g)

reset_game()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.fill((255, 255, 255))

    # screen for typing in your name
    if game_state == "NAME_INPUT":
        ui.draw_text("Enter Name:", (80, 200))
        ui.draw_text(username, (80, 260), color=(0, 0, 255))
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username != "":
                    game_state = "MENU"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 10: username += event.unicode

    # home screen with menu options
    elif game_state == "MENU":
        ui.draw_text("RACER ARCADE", (50, 100))
        if ui.draw_button("PLAY", pygame.Rect(100, 200, 200, 50)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]: 
                reset_game()
                game_state = "GAME"
        if ui.draw_button("LEADERBOARD", pygame.Rect(100, 270, 200, 50)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]: game_state = "LEADERBOARD"
        if ui.draw_button("SETTINGS", pygame.Rect(100, 340, 200, 50)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]: game_state = "SETTINGS"
        if ui.draw_button("QUIT", pygame.Rect(100, 410, 200, 50)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]: pygame.quit(); sys.exit()

    # settings menu logic
    elif game_state == "SETTINGS":
        ui.draw_text("Settings", (120, 50))
        
        # toggle volume
        sound_status = "ON" if settings["sound"] else "OFF"
        if ui.draw_button(f"Sound: {sound_status}", pygame.Rect(100, 130, 200, 40)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                settings["sound"] = not settings["sound"]
                update_music()
                time.sleep(0.2)

        # change difficulty
        diff_txt = f"Diff: {settings['difficulty']}"
        if ui.draw_button(diff_txt, pygame.Rect(100, 190, 200, 40)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                levels = ["Easy", "Medium", "Hard"]
                settings["difficulty"] = levels[(levels.index(settings["difficulty"]) + 1) % 3]
                time.sleep(0.2)

        # change car paint
        color_txt = f"Car: {settings['car_color']}"
        if ui.draw_button(color_txt, pygame.Rect(100, 250, 200, 40)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]:
                colors = ["RED", "BLUE", "GREEN"]
                settings["car_color"] = colors[(colors.index(settings["car_color"]) + 1) % 3]
                time.sleep(0.2)

        if ui.draw_button("BACK & SAVE", pygame.Rect(100, 400, 200, 40)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]: 
                save_settings(settings)
                game_state = "MENU"
                
    # leaderboard display
    elif game_state == "LEADERBOARD":
        ui.draw_text("Top 10", (130, 50))
        scores = load_leaderboard()
        for i, s in enumerate(scores):
            # show rank, name, points and distance
            text_str = f"{i+1}. {s['name']} | Pts: {s['score']} | Dist: {s['distance']}m"
            ui.draw_text(text_str, (20, 120 + i*30), "small")
            
        if ui.draw_button("BACK", pygame.Rect(100, 500, 200, 40)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]: game_state = "MENU"

    # main gameplay loop
    elif game_state == "GAME":
        # calculate travel and auto-increase difficulty
        distance += (speed / 20)
        speed += 0.001 
        
        player.move()
        for e in enemies:
            if e.move(): score += 1
        for c in coins: c.move(speed)
        for h in hazards: h.move(speed)
        for p in powerups: p.move(speed)

        # render background and sprites
        DISPLAYSURF.blit(background_img, (0,0))
        for entity in all_sprites:
            DISPLAYSURF.blit(entity.image, entity.rect)
        
        # heads up display
        ui.draw_text(f"Coins: {coin_score}", (10, 10), "small")
        ui.draw_text(f"Lives: {player.lives}", (10, 35), "small", (0, 150, 0))
        ui.draw_text(f"{int(distance)}m", (340, 10), "small")
        
        # simple distance event
        if int(distance) > 0 and int(distance) % 1000 < 20:
            ui.draw_text("CHECKPOINT REACHED!", (50, 200), "large", (0, 255, 0))

        # powerup timers
        if player.shield_active: 
            ui.draw_text("PWR: SHIELD", (10, 60), "small", (0, 0, 255))
        elif player.nitro_active:
            time_left = max(0, 3 - (time.time() - player.nitro_timer))
            ui.draw_text(f"PWR: NITRO ({time_left:.1f}s)", (10, 60), "small", (255, 150, 0))

        # hit a coin
        c_hit = pygame.sprite.spritecollideany(player, coins)
        if c_hit:
            coin_score += c_hit.value
            c_hit.reset()

        # hit oil or pothole
        h_hit = pygame.sprite.spritecollideany(player, hazards)
        if h_hit:
            if h_hit.type == "Oil":
                speed = max(3, speed - 3)
            elif h_hit.type == "Pothole":
                if player.shield_active:
                    player.shield_active = False 
                    play_crash_sound()
                elif player.lives > 0:
                    player.lives -= 1 
                    play_crash_sound()
                else:
                    # no safety nets left, game over
                    play_crash_sound()
                    final_score_display = (score * 10) + (coin_score * 5) + int(distance)
                    save_score(username, final_score_display, distance)
                    game_state = "GAME_OVER"
            h_hit.reset()

        # pickup a booster
        p_hit = pygame.sprite.spritecollideany(player, powerups)
        if p_hit:
            if p_hit.type == "Shield": 
                player.shield_active = True
                player.nitro_active = False
            elif p_hit.type == "Nitro": 
                player.nitro_active = True
                player.shield_active = False
                player.nitro_timer = time.time()
            elif p_hit.type == "Repair": 
                player.lives += 1 
            p_hit.reset()

        # nitro expiration check
        if player.nitro_active and time.time() - player.nitro_timer > 3:
            player.nitro_active = False

        # enemy collision logic
        if pygame.sprite.spritecollideany(player, enemies):
            if player.shield_active:
                player.shield_active = False
                play_crash_sound()
                pygame.sprite.spritecollideany(player, enemies).reset()
            elif player.lives > 0:
                player.lives -= 1
                play_crash_sound()
                pygame.sprite.spritecollideany(player, enemies).reset()
            else:
                play_crash_sound()
                # formula for final score calculation
                final_score_display = (score * 10) + (coin_score * 5) + int(distance)
                save_score(username, final_score_display, distance)
                game_state = "GAME_OVER"

    # end screen
    elif game_state == "GAME_OVER":
        ui.draw_text("GAME OVER", (90, 150), color=(200, 0, 0))
        ui.draw_text(f"Total Score: {final_score_display}", (110, 220), "small")
        if ui.draw_button("RETRY", pygame.Rect(100, 300, 200, 50)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]: reset_game(); game_state = "GAME"
        if ui.draw_button("MENU", pygame.Rect(100, 370, 200, 50)).collidepoint(pygame.mouse.get_pos()):
            if pygame.mouse.get_pressed()[0]: game_state = "MENU"

    # update screen and lock framerate
    pygame.display.update()
    FramePerSec.tick(FPS)