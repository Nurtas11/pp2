# tools.py
import pygame
import math

def drawSquare(surface, start, end, color, thickness):
    # Find how far the user dragged
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    
    # Pick the smaller side to enforce a perfect square
    size = min(abs(dx), abs(dy))
    
    size_x = -size if dx < 0 else size
    size_y = -size if dy < 0 else size
    
    rect_x = min(start[0], start[0] + size_x)
    rect_y = min(start[1], start[1] + size_y)
    
    pygame.draw.rect(surface, color, (rect_x, rect_y, size, size), thickness)

def drawRightTriangle(surface, start, end, color, thickness):
    # A right triangle with the 90-degree angle at the bottom-left
    p1 = start                       # Top-left corner
    p2 = (start[0], end[1])          # Bottom-left corner
    p3 = end                         # Bottom-right corner
    pygame.draw.polygon(surface, color, [p1, p2, p3], thickness)

def drawEqTriangle(surface, start, end, color, thickness):
    # Calculate the height of an equilateral triangle based on base width
    base_width = end[0] - start[0]
    p1 = start                                   
    p2 = (end[0], start[1])                      
    mid_x = (start[0] + end[0]) / 2             
    height = abs(base_width) * math.sqrt(3) / 2  
    p3 = (mid_x, start[1] - height)
    
    pygame.draw.polygon(surface, color, [p1, p2, p3], thickness)

def drawRhombus(surface, start, end, color, thickness):
    # Diamond shape based on the drag bounding box
    center_x = (start[0] + end[0]) / 2
    center_y = (start[1] + end[1]) / 2
    half_w = abs(end[0] - start[0]) / 2
    half_h = abs(end[1] - start[1]) / 2
    
    top    = (center_x, center_y - half_h)
    right  = (center_x + half_w, center_y)
    bottom = (center_x, center_y + half_h)
    left   = (center_x - half_w, center_y)
    
    pygame.draw.polygon(surface, color, [top, right, bottom, left], thickness)

def drawToolbar(screen, tool, custom_color, thickness):
    # Draw dark background for toolbar
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, 640, 60))
    font = pygame.font.SysFont(None, 20)
    
    # Split tools into two rows
    tools_list_1 = [
        ('1:Pencil', 'draw'), ('2:Rect', 'rectangle'), ('3:Circ', 'circle'), 
        ('4:Eraser', 'eraser'), ('5:Sq', 'square'), ('6:RTri', 'right_triangle')
    ]
    tools_list_2 = [
        ('7:ETri', 'eq_triangle'), ('8:Rhom', 'rhombus'), ('9:Line', 'line'), 
        ('0:Fill', 'fill'), ('T:Text', 'text')
    ]
    
    # Render Row 1 tools
    for i, (label, t) in enumerate(tools_list_1):
        color = (255, 255, 0) if t == tool else (200, 200, 200)
        text = font.render(label, True, color)
        screen.blit(text, (10 + i * 85, 10))
        
    # Render Row 2 tools
    for i, (label, t) in enumerate(tools_list_2):
        color = (255, 255, 0) if t == tool else (200, 200, 200)
        text = font.render(label, True, color)
        screen.blit(text, (10 + i * 85, 35))
        
    # Render Color Preview Block
    pygame.draw.rect(screen, custom_color, (590, 15, 30, 30))
    
    # Render Brush Size Instructions
    size_label = font.render(f"Size: {thickness}", True, (200, 200, 200))
    keys_label = font.render("(Up/Down)", True, (150, 150, 150))
    screen.blit(size_label, (510, 15))
    screen.blit(keys_label, (510, 35))

def flood_fill(surface, pos, fill_color):
    """
    Fills an enclosed area using a span-fill algorithm to avoid recursion limits.
    """
    target_color = surface.get_at(pos)
    fill_color_mapped = surface.map_rgb(fill_color)
    
    if target_color == fill_color_mapped:
        return
        
    stack = [pos]
    width, height = surface.get_size()
    
    while stack:
        x, y = stack.pop()
        
        if surface.get_at((x, y)) == target_color:
            # Find left bound
            lx = x
            while lx > 0 and surface.get_at((lx - 1, y)) == target_color:
                lx -= 1
            
            # Find right bound
            rx = x
            while rx < width - 1 and surface.get_at((rx + 1, y)) == target_color:
                rx += 1
            
            # Fill row and check adjacent rows
            for i in range(lx, rx + 1):
                surface.set_at((i, y), fill_color)
                if y > 0 and surface.get_at((i, y - 1)) == target_color:
                    stack.append((i, y - 1))
                if y < height - 1 and surface.get_at((i, y + 1)) == target_color:
                    stack.append((i, y + 1))