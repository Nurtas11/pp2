import pygame

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
    tool = 'draw'  # can be 'draw', 'rectangle', 'circle', 'eraser'
    rect_start = None   # where the user started drawing a rectangle
    circle_start = None # where the user started drawing a circle
    shapes = []         # list of all finished shapes to redraw every frame
    custom_color = (0, 0, 255)  # default custom color is blue

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

# Draw a simple toolbar bar at the top of the screen
def drawToolbar(screen, tool, custom_color, mode):
    # Draw toolbar background
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, 640, 30))

    # Label for each tool
    font = pygame.font.SysFont(None, 20)

    # Show tool options with highlight for the active one
    tools_list = [('1:Draw', 'draw'), ('2:Rect', 'rectangle'), ('3:Circle', 'circle'), ('4:Eraser', 'eraser')]
    x_pos = 5
    for label, t in tools_list:
        # Highlight the currently selected tool
        if t == tool:
            color = (255, 255, 0)  # yellow for active tool
        else:
            color = (200, 200, 200)
        text = font.render(label, True, color)
        screen.blit(text, (x_pos, 8))
        x_pos += 80

    # Show current color as a small box on the right
    pygame.draw.rect(screen, custom_color, (580, 5, 20, 20))
    color_label = font.render('Color:', True, (200, 200, 200))
    screen.blit(color_label, (530, 8))

    # Show color key hints
    hint_font = pygame.font.SysFont(None, 17)
    hint = font.render('R/G/B/Y/P/W/C = colors', True, (150, 150, 150))
    screen.blit(hint, (320, 8))


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
