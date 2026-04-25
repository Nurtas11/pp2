import pygame, sys
from pygame.locals import *
import random, time

# initialization
pygame.init()

# setting fps
FPS = 60
FramePerSec = pygame.time.Clock()

# colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# configs 
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COIN_SCORE = 0  

# NEW config
# Every time the player collects this many coins, enemies get faster
COINS_PER_SPEED_BOOST = 5

# necessary fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# loading background
background = pygame.image.load("AnimatedStreet.png")

# screen setup
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        # Randomize spawn at the top within road boundaries
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED) # Move downward based on current game speed
        if (self.rect.bottom > 600):
            SCORE += 1              # score is added if enemy is dodged
            self.rect.top = 0       # reset to top for reuse
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Coin.png")
        self.rect = self.image.get_rect()
        #initial spawn above the screen and setting random position in X-axis
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)

        # NEW coin weights
        # Pick a random weight for this coin using weighted probability.
        # "weights" in random.choices means higher number = more likely to be chosen.
        # So weight=1 coins are rare (worth 3 points), weight=5 coins are common (worth 1 point).
        coin_types = [
            {"value": 1, "weight": 5},   # Common coin  - worth 1 point
            {"value": 2, "weight": 3},   # Uncommon coin - worth 2 points
            {"value": 3, "weight": 1},   # Rare coin    - worth 3 points
        ]

        # random.choices picks one item from coin_types using the weights list
        chosen = random.choices(
            coin_types,
            weights=[c["weight"] for c in coin_types],
            k=1
        )[0]  # [0] because random.choices returns a list, we just want the first item

        # Store this coin's value so we can add it to the score on pickup
        self.value = chosen["value"]

        # Tint the coin image to show its rarity:
        # Green = common (1pt), Blue = uncommon (2pt), Red = rare (3pt)
        tint_colors = {1: GREEN, 2: BLUE, 3: RED}
        tint = tint_colors[self.value]

        # Make a copy of the image so we don't change the original for all coins
        self.image = self.image.copy()

        # Fill the coin with a tint color while keeping transparency
        # BLEND_MULT multiplies the pixel colors together, giving a tinted look
        tint_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        tint_surface.fill(tint + (180,))  # Add alpha value to make the tint semi-transparent
        self.image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def move(self):
        self.rect.move_ip(0, SPEED) 
        #loop coin back to top if player misses it
        if (self.rect.top > SCREEN_HEIGHT):
            self.rect.top = 0
            #setting coin to random pos in x-axis
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)



class Racer(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Player.png")  # Still uses the same Player.png image
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520) # Starting position near the bottom
       
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        #horizontal movement with boundary checks
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                  self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH:        
              if pressed_keys[K_RIGHT]:
                  self.rect.move_ip(5, 0)

# Instantiate game objects

P1 = Racer()
E1 = Enemy()
C1 = Coin()

# create Sprite Groups for collision detection and batch rendering
enemies = pygame.sprite.Group()
#group for only enemies sprites
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

#group for all sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# speed increases every second
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# new: track how many coins the player had last time we checked for a boost 
# This lets us know when the player crosses a new multiple of COINS_PER_SPEED_BOOST
last_coin_boost_milestone = 0

#game loop
while True:
    # event handling
    for event in pygame.event.get():
        if event.type == INC_SPEED:
              SPEED += 0.5      
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # drawing background
    DISPLAYSURF.blit(background, (0, 0))
    
    #pdate UI text for distance and collected coins
    scores = font_small.render(str(SCORE), True, BLACK)
    coin_display = font_small.render("Coins: " + str(COIN_SCORE), True, BLACK)
    
    DISPLAYSURF.blit(scores, (10, 10))
    DISPLAYSURF.blit(coin_display, (SCREEN_WIDTH - 100, 10))

    # new: coin values UI
    hint = font_small.render("G=1pt B=2pt R=3pt", True, BLACK)
    DISPLAYSURF.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 10))

    #Move and draw all items in the sprite group
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    #detect if player touches a coin
    coin_hit = pygame.sprite.spritecollideany(P1, coins)
    if coin_hit:
        # add the coin's value instead of always adding 1
        COIN_SCORE += coin_hit.value

        # Teleport coin back to top to simulate a new spawn
        coin_hit.rect.top = 0
        coin_hit.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)

        # re-roll the coin's value and tint when it respawns
        # We call __init__ again by creating a fresh Coin and replacing the old one.
        # This gives the coin a new random weight every time it is collected.
        new_coin = Coin()
        coins.remove(coin_hit)
        all_sprites.remove(coin_hit)
        coin_hit.kill()
        coins.add(new_coin)
        all_sprites.add(new_coin)

    #  check if the player reached a coin milestone 
    # Integer division (//) tells us how many full milestones the player has reached.
    # Example: if COINS_PER_SPEED_BOOST = 5 and COIN_SCORE = 10, milestone = 2.
    current_milestone = COIN_SCORE // COINS_PER_SPEED_BOOST

    if current_milestone > last_coin_boost_milestone:
        # The player just passed a new milestone, so speed up the enemies
        SPEED += 1                        # Increase global enemy speed
        last_coin_boost_milestone = current_milestone  # Remember this milestone

    #detect collision with enemy 
    if pygame.sprite.spritecollideany(P1, enemies):
          time.sleep(1) # Brief pause for visual impact
          DISPLAYSURF.fill(RED)
          DISPLAYSURF.blit(game_over, (30, 250))
          pygame.display.update()
          # Clean up sprites and exit
          for entity in all_sprites:
                entity.kill() 
          time.sleep(2)
          pygame.quit()
          sys.exit()        
    
    # refresh display
    #update is used when we need to refresh only some specific area
    #flip is used for refreshing whole screen
    pygame.display.update()
    FramePerSec.tick(FPS)
