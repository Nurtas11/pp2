radius = 25
x = 300.0  # current pos
y = 300.0
target_x = 300.0  # where the ball is heading
target_y = 300.0
step = 20  # how far each key press moves the target

def press_up():
    global target_y
    if target_y - radius - step >= 0:  # dont go past top edge
        target_y = target_y - step

def press_down(screen_height):
    global target_y
    if target_y + radius + step <= screen_height:  # dont go past bottom edge
        target_y = target_y + step

def press_left():
    global target_x
    if target_x - radius - step >= 0:  # dont go past left edge
        target_x = target_x - step

def press_right(screen_width):
    global target_x
    if target_x + radius + step <= screen_width:  # dont go past right edge
        target_x = target_x + step

def update():
    global x, y
    x = x + (target_x - x) * 0.2  # move 20% closer to target each frame
    y = y + (target_y - y) * 0.2  # same for y
