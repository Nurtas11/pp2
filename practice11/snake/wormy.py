# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

FPS = 15
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

# wall color so we can draw it separately
WALLCOLOR = (100, 100, 100)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

# how many apples to eat before going to next level
APPLES_PER_LEVEL = 3

# how much to speed up each level (added to FPS base)
SPEED_INCREASE = 3

# food types
# Each food type has: name, color, points, weight, lifetime (seconds)
# weight means how likely it is to appear (higher = more common)
# lifetime is how many seconds before it disappears (None = never disappears)
FOOD_TYPES = [
    {'name': 'apple',    'color': (255,   0,   0), 'points': 10, 'weight': 50, 'lifetime': None},
    {'name': 'banana',   'color': (255, 255,   0), 'points': 20, 'weight': 30, 'lifetime': 5},
    {'name': 'cherry',   'color': (200,   0, 100), 'points': 30, 'weight': 15, 'lifetime': 4},
    {'name': 'diamond',  'color': (  0, 255, 255), 'points': 50, 'weight':  5, 'lifetime': 3},
]
# total weight is used to calculate probability
TOTAL_WEIGHT = 0
for food in FOOD_TYPES:
    TOTAL_WEIGHT += food['weight']


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def pickFoodType():
    # pick a random food type based on weight
    # higher weight = picked more often
    roll = random.randint(1, TOTAL_WEIGHT)
    total = 0
    for food in FOOD_TYPES:
        total += food['weight']
        if roll <= total:
            return food
    # fallback: return the first food (should never reach here)
    return FOOD_TYPES[0]


def makeFood(wormCoords):
    # pick a food type and a random location, then record spawn time
    foodType = pickFoodType()
    location = getRandomLocation(wormCoords)
    spawnTime = pygame.time.get_ticks()  # current time in milliseconds
    # combine location info with food info into one dictionary
    food = {
        'x':        location['x'],
        'y':        location['y'],
        'color':    foodType['color'],
        'points':   foodType['points'],
        'lifetime': foodType['lifetime'],  # seconds before it disappears (or None)
        'spawnTime': spawnTime,
        'name':     foodType['name'],
    }
    return food


def isFoodExpired(food):
    # check if the food has been on screen too long
    if food['lifetime'] is None:
        return False  # this food never disappears
    # how many milliseconds have passed since the food spawned
    timeAlive = pygame.time.get_ticks() - food['spawnTime']
    # convert lifetime from seconds to milliseconds for comparison
    lifetimeMs = food['lifetime'] * 1000
    return timeAlive >= lifetimeMs


def getFoodTimeLeft(food):
    # returns how many seconds are left before the food disappears
    if food['lifetime'] is None:
        return None  # food never expires
    timeAlive = pygame.time.get_ticks() - food['spawnTime']
    lifetimeMs = food['lifetime'] * 1000
    timeLeftMs = lifetimeMs - timeAlive
    if timeLeftMs < 0:
        timeLeftMs = 0
    # convert back to seconds
    return timeLeftMs / 1000


def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place (not on wall or worm).
    # NEW: use makeFood() instead of getRandomLocation() to get a full food object
    apple = makeFood(wormCoords)

    # level starts at 1, score and apples eaten start at 0
    level = 1
    score = 0
    applesEaten = 0

    # current speed depends on level
    currentFPS = FPS

    # bonus food list
    # bonus foods appear randomly and disappear after a short time
    bonusFoods = []

    # how often a bonus food tries to spawn (in frames)
    bonusSpawnTimer = 0
    # try to spawn a bonus food every 3 seconds (FPS * 3 frames)
    BONUS_SPAWN_INTERVAL = FPS * 3

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if worm hit the border wall (cells 0 and max are walls now)
        if wormCoords[HEAD]['x'] == 0 or wormCoords[HEAD]['x'] == CELLWIDTH - 1 or wormCoords[HEAD]['y'] == 0 or wormCoords[HEAD]['y'] == CELLHEIGHT - 1:
            return # game over

        # check if worm hit itself
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over

        # check if worm has eaten an apple
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            # NEW: use makeFood() to create a new food with random type
            apple = makeFood(wormCoords)
            # NEW: give points based on food type instead of always 10
            score += apple['points']
            applesEaten += 1      # count how many apples eaten this level

            # check if snake ate enough apples to level up
            if applesEaten >= APPLES_PER_LEVEL:
                level += 1
                applesEaten = 0                        # reset apple counter for new level
                currentFPS = FPS + (level - 1) * SPEED_INCREASE  # speed up the game
        else:
            del wormCoords[-1] # remove worm's tail segment

        #  check if main apple has expired 
        if isFoodExpired(apple):
            # replace it with a fresh food at a new location
            apple = makeFood(wormCoords)

        #  spawn bonus food on a timer
        bonusSpawnTimer += 1
        if bonusSpawnTimer >= BONUS_SPAWN_INTERVAL:
            bonusSpawnTimer = 0  # reset the timer
            # only spawn a bonus food if it has a short lifetime (not None)
            newBonus = makeFood(wormCoords)
            # keep trying until we get a food that expires (not the plain apple)
            while newBonus['lifetime'] is None:
                newBonus = makeFood(wormCoords)
            bonusFoods.append(newBonus)

        # check if worm ate any bonus food 
        bonusFoodsToKeep = []  # build a new list without eaten or expired foods
        for bonus in bonusFoods:
            if bonus['x'] == wormCoords[HEAD]['x'] and bonus['y'] == wormCoords[HEAD]['y']:
                # worm ate this bonus food
                score += bonus['points']
                # don't add it to bonusFoodsToKeep so it disappears
            elif isFoodExpired(bonus):
                # food timer ran out, remove it (don't add to keep list)
                pass
            else:
                # food is still valid, keep it
                bonusFoodsToKeep.append(bonus)
        bonusFoods = bonusFoodsToKeep  # replace the list with the updated one

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWalls()         # draw the border walls on top of the grid
        drawWorm(wormCoords)
        # NEW: draw the main food using the new drawFood function
        drawFood(apple)
        # NEW: draw all bonus foods and their timers
        for bonus in bonusFoods:
            drawFood(bonus)
            drawFoodTimer(bonus)
        drawScore(score, level)   # pass level to display both score and level
        pygame.display.update()
        FPSCLOCK.tick(currentFPS)  # use currentFPS so speed changes with level


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation(wormCoords):
    # keep trying until we find a spot that is not a wall and not on the worm
    while True:
        x = random.randint(1, CELLWIDTH - 2)   # 1 to CELLWIDTH-2 avoids wall columns
        y = random.randint(1, CELLHEIGHT - 2)  # 1 to CELLHEIGHT-2 avoids wall rows

        # check that this position is not occupied by any part of the worm
        onWorm = False
        for segment in wormCoords:
            if segment['x'] == x and segment['y'] == y:
                onWorm = True
                break

        # if not on worm, this spot is good
        if not onWorm:
            return {'x': x, 'y': y}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return


def drawScore(score, level):
    # draw the score in the top right corner
    scoreSurf = BASICFONT.render('Score: %s' % score, True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the current level just below the score
    levelSurf = BASICFONT.render('Level: %s' % level, True, WHITE)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 120, 30)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawWorm(wormCoords):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, GREEN, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


# draw any food using its own color 
def drawFood(food):
    x = food['x'] * CELLSIZE
    y = food['y'] * CELLSIZE
    foodRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    # draw the outer square with the food's color
    pygame.draw.rect(DISPLAYSURF, food['color'], foodRect)
    # draw a smaller dark square inside so it looks distinct
    innerRect = pygame.Rect(x + 5, y + 5, CELLSIZE - 10, CELLSIZE - 10)
    pygame.draw.rect(DISPLAYSURF, BLACK, innerRect)


#  draw a countdown timer above a food item 
def drawFoodTimer(food):
    timeLeft = getFoodTimeLeft(food)
    if timeLeft is None:
        return  # no timer to draw for this food
    # round the time to 1 decimal so it doesn't look jittery
    timeLeft = round(timeLeft, 1)
    # make a small text surface showing the time left
    timerSurf = BASICFONT.render(str(timeLeft), True, food['color'])
    x = food['x'] * CELLSIZE
    y = food['y'] * CELLSIZE - 18  # draw just above the food cell
    DISPLAYSURF.blit(timerSurf, (x, y))


def drawWalls():
    # draw the top and bottom border rows
    for x in range(CELLWIDTH):
        topRect = pygame.Rect(x * CELLSIZE, 0, CELLSIZE, CELLSIZE)
        botRect = pygame.Rect(x * CELLSIZE, (CELLHEIGHT - 1) * CELLSIZE, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, WALLCOLOR, topRect)
        pygame.draw.rect(DISPLAYSURF, WALLCOLOR, botRect)

    # draw the left and right border columns
    for y in range(CELLHEIGHT):
        leftRect = pygame.Rect(0, y * CELLSIZE, CELLSIZE, CELLSIZE)
        rightRect = pygame.Rect((CELLWIDTH - 1) * CELLSIZE, y * CELLSIZE, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, WALLCOLOR, leftRect)
        pygame.draw.rect(DISPLAYSURF, WALLCOLOR, rightRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
