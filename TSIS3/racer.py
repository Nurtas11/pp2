import pygame
import random
import os

# basic colors for tinting and drawing
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
ASSET_PATH = "assets"

# center coordinates for the three road lanes
LANES = [70, 200, 330]

class Player(pygame.sprite.Sprite):
    def __init__(self, color_name="RED"):
        super().__init__()
        # load the car image from assets folder
        img_path = os.path.join(ASSET_PATH, "Player.png")
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect()
        # starting position near the bottom
        self.rect.center = (160, 520)
        
        # internal flags for powerups and health
        self.lives = 0           
        self.shield_active = False
        self.nitro_active = False
        self.nitro_timer = 0
        
        # map string names from settings to actual RGB colors
        color_map = {"RED": RED, "BLUE": BLUE, "GREEN": GREEN}
        tint = color_map.get(color_name, RED)
        
        # creating a surface to overlay the color on the car sprite
        tint_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        tint_surf.fill(tint + (255,)) 
        self.image.blit(tint_surf, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

    def move(self):
        # get keys currently being held down
        pressed_keys = pygame.key.get_pressed()
        # change velocity if nitro powerup is on
        move_speed = 10 if self.nitro_active else 5
        
        # left and right movement with screen boundaries
        if self.rect.left > 0 and pressed_keys[pygame.K_LEFT]:
            self.rect.move_ip(-move_speed, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[pygame.K_RIGHT]:
            self.rect.move_ip(move_speed, 0)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # load the enemy car sprite
        img_path = os.path.join(ASSET_PATH, "Enemy.png")
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect()
        self.speed = speed
        self.reset()

    def reset(self):
        # move enemy back to top in a random lane
        self.rect.center = (random.choice(LANES), random.randint(-300, -100))

    def move(self):
        # scroll enemy down the screen
        self.rect.move_ip(0, self.speed)
        # if it goes off bottom, reset it to the top
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()
            return True 
        return False

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        img_path = os.path.join(ASSET_PATH, "Coin.png")
        self.original_image = pygame.image.load(img_path)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        # setup first coin state
        self.reset()

    def reset(self):
        # pick a lane and random height off-screen
        self.rect.center = (random.choice(LANES), random.randint(-500, -50))
        
        # coin rarity system: green(common), blue(rare), red(ultra)
        coin_types = [
            {"val": 1, "w": 5, "c": GREEN}, 
            {"val": 2, "w": 3, "c": BLUE},  
            {"val": 3, "w": 1, "c": RED}   
        ]
        # pick one based on the weights 'w'
        chosen = random.choices(coin_types, weights=[c["w"] for c in coin_types], k=1)[0]
        self.value = chosen["val"]
        
        # apply the color tint so player knows the value
        self.image = self.original_image.copy()
        tint_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        tint_surf.fill(chosen["c"] + (200,))
        self.image.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def move(self, speed):
        # fall down at road speed
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

class Hazard(pygame.sprite.Sprite):
    def __init__(self, hazard_type):
        super().__init__()
        self.type = hazard_type 
        # use the hazard name to find the png file
        img_path = os.path.join(ASSET_PATH, f"{hazard_type}.png")
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        # hazards spawn further apart than coins
        self.rect.center = (random.choice(LANES), random.randint(-1000, -200))

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, p_type):
        super().__init__()
        self.type = p_type 
        # nitro, shield, or repair images
        img_path = os.path.join(ASSET_PATH, f"{p_type}.png")
        self.image = pygame.image.load(img_path)
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self):
        # make powerups very rare by spawning them far up
        self.rect.center = (random.choice(LANES), random.randint(-1500, -500))

    def move(self, speed):
        self.rect.move_ip(0, speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset()