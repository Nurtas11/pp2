import pygame
import math  # We need math for calculating triangle points

def main():
    # Setup Pygame window and clock
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    # Initial variables
    radius = 15
    x = 0
    y = 0
    mode = 'blue'
    points = []

    # New variables for the new tools
    tool = 'draw'  # can be 'draw', 'rectangle', 'circle', 'eraser', 'square', 'right_triangle', 'eq_triangle', 'rhombus'
    rect_start = None   # where the user started drawing a rectangle
    circle_start = None # where the user started drawing a circle
    shapes = []         # list of all finished shapes to redraw every frame
    custom_color = (0, 0, 255)  # default custom color is blue

    # Start positions for the new shapes
    square_start = None       # where the user started drawing a square
    right_tri_start = None    # where the user started drawing a right triangle
    eq_tri_start = None       # where the user started drawing an equilateral triangle
    rhombus_start = None      # where the user started drawing a rhombus

    while True:
        # Handle key modifiers
        pressed = pygame.key.get_pressed()
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():
            # Determine if X was clicked, or Ctrl+W or Alt+F4 was used
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return

                #determine if a letter key was pressed to change color
                if event.key == pygame.K_r:
                    mode = 'red'
                    custom_color = (255, 0, 0)
                elif event.key == pygame.K_g:
                    mode = 'green'
                    custom_color = (0, 255, 0)
                elif event.key == pygame.K_b:
                    mode = 'blue'
                    custom_color = (0, 0, 255)

                #key shortcuts to switch tools
                # Press 1 for freehand draw, 2 for rectangle, 3 for circle, 4 for eraser
                if event.key == pygame.K_1:
                    tool = 'draw'
                elif event.key == pygame.K_2:
                    tool = 'rectangle'
                elif event.key == pygame.K_3:
                    tool = 'circle'
                elif event.key == pygame.K_4:
                    tool = 'eraser'

                # Press 5, 6, 7, 8 for the new shape tools
                elif event.key == pygame.K_5:
                    tool = 'square'
                elif event.key == pygame.K_6:
                    tool = 'right_triangle'
                elif event.key == pygame.K_7:
                    tool = 'eq_triangle'
                elif event.key == pygame.K_8:
                    tool = 'rhombus'

                #color selection with number keys + shift
                #olor  selection
                if event.key == pygame.K_y:
                    mode = 'custom'
                    custom_color = (255, 255, 0)
                elif event.key == pygame.K_p:
                    mode = 'custom'
                    custom_color = (255, 0, 255)
                elif event.key == pygame.K_w:
                    mode = 'custom'
                    custom_color = (255, 255, 255)
                elif event.key == pygame.K_c:
                    mode = 'custom'
                    custom_color = (0, 255, 255)

            # mouse click for radius
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click grows radius
                    radius = min(200, radius + 1)
                elif event.button == 3: # Right click shrinks radius
                    radius = max(1, radius - 1)

                # When user presses left mouse button, record start position for shapes
                if event.button == 1:
                    if tool == 'rectangle':
                        rect_start = event.pos
                    elif tool == 'circle':
                        circle_start = event.pos
                    # Record the start position for each new shape
                    elif tool == 'square':
                        square_start = event.pos
                    elif tool == 'right_triangle':
                        right_tri_start = event.pos
                    elif tool == 'eq_triangle':
                        eq_tri_start = event.pos
                    elif tool == 'rhombus':
                        rhombus_start = event.pos

            # When user releases mouse button, finish drawing the shape
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if tool == 'rectangle' and rect_start is not None:
                        # Save the finished rectangle: (type, start, end, color)
                        shapes.append(('rectangle', rect_start, event.pos, custom_color))
                        rect_start = None
                    elif tool == 'circle' and circle_start is not None:
                        # Save the finished circle: (type, center, radius, color)
                        # Calculate radius as distance from start to release point
                        dx = event.pos[0] - circle_start[0]
                        dy = event.pos[1] - circle_start[1]
                        r = int((dx**2 + dy**2) ** 0.5)
                        shapes.append(('circle', circle_start, r, custom_color))
                        circle_start = None

                    # Finish drawing a square when mouse is released
                    elif tool == 'square' and square_start is not None:
                        shapes.append(('square', square_start, event.pos, custom_color))
                        square_start = None

                    # Finish drawing a right triangle when mouse is released
                    elif tool == 'right_triangle' and right_tri_start is not None:
                        shapes.append(('right_triangle', right_tri_start, event.pos, custom_color))
                        right_tri_start = None

                    # Finish drawing an equilateral triangle when mouse is released
                    elif tool == 'eq_triangle' and eq_tri_start is not None:
                        shapes.append(('eq_triangle', eq_tri_start, event.pos, custom_color))
                        eq_tri_start = None

                    # Finish drawing a rhombus when mouse is released
                    elif tool == 'rhombus' and rhombus_start is not None:
                        shapes.append(('rhombus', rhombus_start, event.pos, custom_color))
                        rhombus_start = None

            # Drawing logic: add point to list on mouse movement
            if event.type == pygame.MOUSEMOTION:
                position = event.pos
                # Only collect freehand points when using draw or eraser tool
                if tool == 'draw' or tool == 'eraser':
                    points = points + [position]
                    points = points[-256:] # Keep only the last 256 points

        # Refresh screen
        screen.fill((0, 0, 0))

        # Draw all saved shapes first
        for shape in shapes:
            if shape[0] == 'rectangle':
                # shape = ('rectangle', start, end, color)
                start_pos = shape[1]
                end_pos = shape[2]
                color = shape[3]
                rect_x = min(start_pos[0], end_pos[0])
                rect_y = min(start_pos[1], end_pos[1])
                rect_w = abs(end_pos[0] - start_pos[0])
                rect_h = abs(end_pos[1] - start_pos[1])
                pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h), 2)
            elif shape[0] == 'circle':
                # shape = ('circle', center, radius, color)
                pygame.draw.circle(screen, shape[3], shape[1], shape[2], 2)

            # Draw a saved square
            elif shape[0] == 'square':
                drawSquare(screen, shape[1], shape[2], shape[3])

            # Draw a saved right triangle
            elif shape[0] == 'right_triangle':
                drawRightTriangle(screen, shape[1], shape[2], shape[3])

            # Draw a saved equilateral triangle
            elif shape[0] == 'eq_triangle':
                drawEqTriangle(screen, shape[1], shape[2], shape[3])

            # Draw a saved rhombus
            elif shape[0] == 'rhombus':
                drawRhombus(screen, shape[1], shape[2], shape[3])

        # Draw the shape preview while user is dragging mouse
        mouse_pos = pygame.mouse.get_pos()
        if tool == 'rectangle' and rect_start is not None:
            # Show a preview of the rectangle being drawn
            prev_x = min(rect_start[0], mouse_pos[0])
            prev_y = min(rect_start[1], mouse_pos[1])
            prev_w = abs(mouse_pos[0] - rect_start[0])
            prev_h = abs(mouse_pos[1] - rect_start[1])
            pygame.draw.rect(screen, custom_color, (prev_x, prev_y, prev_w, prev_h), 2)
        elif tool == 'circle' and circle_start is not None:
            # Show a preview of the circle being drawn
            dx = mouse_pos[0] - circle_start[0]
            dy = mouse_pos[1] - circle_start[1]
            preview_r = int((dx**2 + dy**2) ** 0.5)
            pygame.draw.circle(screen, custom_color, circle_start, preview_r, 2)

        # Show a preview of the square being drawn
        elif tool == 'square' and square_start is not None:
            drawSquare(screen, square_start, mouse_pos, custom_color)

        # Show a preview of the right triangle being drawn
        elif tool == 'right_triangle' and right_tri_start is not None:
            drawRightTriangle(screen, right_tri_start, mouse_pos, custom_color)

        # Show a preview of the equilateral triangle being drawn
        elif tool == 'eq_triangle' and eq_tri_start is not None:
            drawEqTriangle(screen, eq_tri_start, mouse_pos, custom_color)

        # Show a preview of the rhombus being drawn
        elif tool == 'rhombus' and rhombus_start is not None:
            drawRhombus(screen, rhombus_start, mouse_pos, custom_color)

        # Draw all points by connecting them
        i = 0
        while i < len(points) - 1:
            if tool == 'eraser':
                # Eraser draws black circles to erase over things
                pygame.draw.circle(screen, (0, 0, 0), points[i], radius * 2)
            else:
                drawLineBetween(screen, i, points[i], points[i + 1], radius, mode)
            i += 1

        # Draw a simple toolbar at the top to show tools and current color
        drawToolbar(screen, tool, custom_color, mode)

        pygame.display.flip()
        clock.tick(60)


# Draw a square shape on the screen
# A square has equal width and height, so we use the smaller side of the drag
def drawSquare(screen, start, end, color):
    # Find how far the user dragged in each direction
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    # Pick the smaller distance so all sides are equal
    size = min(abs(dx), abs(dy))

    # Keep the direction (negative if dragged left/up)
    if dx < 0:
        size_x = -size
    else:
        size_x = size

    if dy < 0:
        size_y = -size
    else:
        size_y = size

    # Calculate the top-left corner of the square
    rect_x = min(start[0], start[0] + size_x)
    rect_y = min(start[1], start[1] + size_y)

    # Draw the square outline
    pygame.draw.rect(screen, color, (rect_x, rect_y, size, size), 2)


# Draw a right triangle on the screen
# A right triangle has one 90-degree corner
# The right angle is at the bottom-left corner
def drawRightTriangle(screen, start, end, color):
    # The three corners of the right triangle:
    # top-left = the start point (where user clicked)
    # bottom-left = directly below the start (the right angle corner)
    # bottom-right = where the user released the mouse
    p1 = start                       # top-left corner
    p2 = (start[0], end[1])          # bottom-left corner (right angle here)
    p3 = end                         # bottom-right corner

    # Draw lines between the three corners
    pygame.draw.polygon(screen, color, [p1, p2, p3], 2)


# Draw an equilateral triangle on the screen
# An equilateral triangle has all three sides the same length
def drawEqTriangle(screen, start, end, color):
    # Use the horizontal drag distance as the base width
    base_width = end[0] - start[0]

    # The base goes from start to (end[0], start[1]) — same vertical level
    p1 = start                                   # bottom-left corner
    p2 = (end[0], start[1])                      # bottom-right corner

    # The top point is centered above the base
    # Height of equilateral triangle = base * sqrt(3) / 2
    mid_x = (start[0] + end[0]) / 2             # center of the base
    height = abs(base_width) * math.sqrt(3) / 2  # exact height for equilateral

    # The top point goes upward (subtract height because y goes down on screen)
    p3 = (mid_x, start[1] - height)

    # Draw lines between the three corners
    pygame.draw.polygon(screen, color, [p1, p2, p3], 2)


# Draw a rhombus (diamond shape) on the screen
# A rhombus has 4 corners: top, bottom, left, right
def drawRhombus(screen, start, end, color):
    # Find the center point between start and end
    center_x = (start[0] + end[0]) / 2
    center_y = (start[1] + end[1]) / 2

    # Half-width and half-height based on the drag distance
    half_w = abs(end[0] - start[0]) / 2
    half_h = abs(end[1] - start[1]) / 2

    # The 4 corners of the rhombus (top, right, bottom, left)
    top    = (center_x, center_y - half_h)
    right  = (center_x + half_w, center_y)
    bottom = (center_x, center_y + half_h)
    left   = (center_x - half_w, center_y)

    # Draw lines between the four corners
    pygame.draw.polygon(screen, color, [top, right, bottom, left], 2)


# Draw a simple toolbar bar at the top of the screen
def drawToolbar(screen, tool, custom_color, mode):
    # Draw toolbar background
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, 640, 30))

    # Label for each tool
    font = pygame.font.SysFont(None, 20)

    # Show tool options with highlight for the active one
    # Added the 4 new tools to the list
    tools_list = [
        ('1:Draw', 'draw'),
        ('2:Rect', 'rectangle'),
        ('3:Circle', 'circle'),
        ('4:Eraser', 'eraser'),
        ('5:Sq', 'square'),
        ('6:RTri', 'right_triangle'),
        ('7:ETri', 'eq_triangle'),
        ('8:Rhom', 'rhombus'),
    ]

    x_pos = 5
    for label, t in tools_list:
        # Highlight the currently selected tool
        if t == tool:
            color = (255, 255, 0)  # yellow for active tool
        else:
            color = (200, 200, 200)
        text = font.render(label, True, color)
        screen.blit(text, (x_pos, 8))
        x_pos += 58  # slightly tighter spacing to fit all 8 tools

    # Show current color as a small box on the right
    pygame.draw.rect(screen, custom_color, (610, 5, 20, 20))
    color_label = font.render('Col:', True, (200, 200, 200))
    screen.blit(color_label, (580, 8))


def drawLineBetween(screen, index, start, end, width, color_mode):
    # Calculate color fading based on the point's index
    c1 = max(0, min(255, 2 * index - 256))
    c2 = max(0, min(255, 2 * index))

    if color_mode == 'blue':
        color = (c1, c1, c2)
    elif color_mode == 'red':
        color = (c2, c1, c1)
    elif color_mode == 'green':
        color = (c1, c2, c1)
    elif color_mode == 'custom':
        # For custom colors just use the full color without fading
        color = (c2, c2, c2)

    # Manual interpolation to draw a smooth "line" of circles
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    for i in range(iterations):
        progress = 1.0 * i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(screen, color, (x, y), width)

# Start the game
if __name__ == "__main__":
    main()
