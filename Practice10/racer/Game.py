
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

    def move(self):
        self.rect.move_ip(0, SPEED) 
        #loop coin back to top if player misses it
        if (self.rect.top > SCREEN_HEIGHT):
            self.rect.top = 0
            #setting coin to random pos in x-axis
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Player.png")
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
P1 = Player()
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

    #Move and draw all items in the sprite group
    for entity in all_sprites:
        entity.move()
        DISPLAYSURF.blit(entity.image, entity.rect)

    #detect if player touches a coin
    coin_hit = pygame.sprite.spritecollideany(P1, coins)
    if coin_hit:
        COIN_SCORE += 1
        # Teleport coin back to top to simulate a new spawn
        coin_hit.rect.top = 0
        coin_hit.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -50)

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