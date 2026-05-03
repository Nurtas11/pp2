# paint.py
import pygame
import datetime

# Import our helper functions from the tools.py module
from tools import drawSquare, drawRightTriangle, drawEqTriangle, drawRhombus, drawToolbar, flood_fill

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((640, 480))
    canvas = pygame.Surface((640, 480))
    canvas.fill((0, 0, 0))
    clock = pygame.time.Clock()

    tool = 'draw' 
    custom_color = (0, 0, 255) 
    
    sizes = [2, 5, 10]
    size_idx = 0
    thickness = sizes[size_idx]

    start_pos = None
    last_pos = None
    is_drawing = False

    is_typing = False
    text_pos = None
    current_text = ""

    while True:
        pressed = pygame.key.get_pressed()
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held: return
                if event.key == pygame.K_F4 and alt_held: return
                
                # Text Tool typing logic
                if is_typing:
                    if event.key == pygame.K_RETURN:
                        font = pygame.font.SysFont(None, 30)
                        text_surf = font.render(current_text, True, custom_color)
                        canvas.blit(text_surf, text_pos)
                        is_typing = False
                    elif event.key == pygame.K_ESCAPE:
                        is_typing = False
                    elif event.key == pygame.K_BACKSPACE:
                        current_text = current_text[:-1]
                    else:
                        if event.unicode.isprintable():
                            current_text += event.unicode
                    continue 

                if event.key == pygame.K_ESCAPE and not is_typing: return

                # Save Canvas logic
                if event.key == pygame.K_s and ctrl_held:
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"canvas_{timestamp}.png"
                    pygame.image.save(canvas, filename)
                    print(f"Canvas saved successfully as {filename}")

                # Brush Size logic
                if event.key == pygame.K_UP:
                    size_idx = min(len(sizes) - 1, size_idx + 1)
                    thickness = sizes[size_idx]
                if event.key == pygame.K_DOWN:
                    size_idx = max(0, size_idx - 1)
                    thickness = sizes[size_idx]

                # Colors
                if event.key == pygame.K_r: custom_color = (255, 0, 0)
                elif event.key == pygame.K_g: custom_color = (0, 255, 0)
                elif event.key == pygame.K_b: custom_color = (0, 0, 255)
                elif event.key == pygame.K_y: custom_color = (255, 255, 0)
                elif event.key == pygame.K_p: custom_color = (255, 0, 255)
                elif event.key == pygame.K_w: custom_color = (255, 255, 255)
                elif event.key == pygame.K_c: custom_color = (0, 255, 255)

                # Tools
                if event.key == pygame.K_1: tool = 'draw'
                elif event.key == pygame.K_2: tool = 'rectangle'
                elif event.key == pygame.K_3: tool = 'circle'
                elif event.key == pygame.K_4: tool = 'eraser'
                elif event.key == pygame.K_5: tool = 'square'
                elif event.key == pygame.K_6: tool = 'right_triangle'
                elif event.key == pygame.K_7: tool = 'eq_triangle'
                elif event.key == pygame.K_8: tool = 'rhombus'
                elif event.key == pygame.K_9: tool = 'line'
                elif event.key == pygame.K_0: tool = 'fill'
                elif event.key == pygame.K_t: 
                    tool = 'text'
                    is_typing = False 

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] < 60: continue # Ignore clicks on toolbar
                    
                if event.button == 1: 
                    if tool in ['draw', 'eraser']:
                        is_drawing = True
                        last_pos = event.pos
                    elif tool == 'fill':
                        flood_fill(canvas, event.pos, custom_color)
                    elif tool == 'text':
                        is_typing = True
                        text_pos = event.pos
                        current_text = ""
                    else:
                        start_pos = event.pos

            if event.type == pygame.MOUSEMOTION:
                if is_drawing:
                    color = (0, 0, 0) if tool == 'eraser' else custom_color
                    pygame.draw.line(canvas, color, last_pos, event.pos, thickness)
                    pygame.draw.circle(canvas, color, event.pos, thickness // 2)
                    last_pos = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if tool in ['draw', 'eraser']:
                        is_drawing = False
                    elif start_pos is not None:
                        end_pos = event.pos
                        
                        if tool == 'rectangle':
                            rect_x = min(start_pos[0], end_pos[0])
                            rect_y = min(start_pos[1], end_pos[1])
                            rect_w = abs(end_pos[0] - start_pos[0])
                            rect_h = abs(end_pos[1] - start_pos[1])
                            pygame.draw.rect(canvas, custom_color, (rect_x, rect_y, rect_w, rect_h), thickness)
                        elif tool == 'circle':
                            r = int(((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2) ** 0.5)
                            draw_thick = thickness if thickness < r else 0
                            pygame.draw.circle(canvas, custom_color, start_pos, r, draw_thick)
                        elif tool == 'line':
                            pygame.draw.line(canvas, custom_color, start_pos, end_pos, thickness)
                        elif tool == 'square':
                            drawSquare(canvas, start_pos, end_pos, custom_color, thickness)
                        elif tool == 'right_triangle':
                            drawRightTriangle(canvas, start_pos, end_pos, custom_color, thickness)
                        elif tool == 'eq_triangle':
                            drawEqTriangle(canvas, start_pos, end_pos, custom_color, thickness)
                        elif tool == 'rhombus':
                            drawRhombus(canvas, start_pos, end_pos, custom_color, thickness)
                        
                        start_pos = None

        screen.blit(canvas, (0, 0))

        # Previews
        mouse_pos = pygame.mouse.get_pos()
        if start_pos is not None:
            if tool == 'rectangle':
                prev_x = min(start_pos[0], mouse_pos[0])
                prev_y = min(start_pos[1], mouse_pos[1])
                prev_w = abs(mouse_pos[0] - start_pos[0])
                prev_h = abs(mouse_pos[1] - start_pos[1])
                pygame.draw.rect(screen, custom_color, (prev_x, prev_y, prev_w, prev_h), thickness)
            elif tool == 'circle':
                prev_r = int(((mouse_pos[0] - start_pos[0])**2 + (mouse_pos[1] - start_pos[1])**2) ** 0.5)
                draw_thick = thickness if thickness < prev_r else 0
                pygame.draw.circle(screen, custom_color, start_pos, prev_r, draw_thick)
            elif tool == 'line':
                pygame.draw.line(screen, custom_color, start_pos, mouse_pos, thickness)
            elif tool == 'square':
                drawSquare(screen, start_pos, mouse_pos, custom_color, thickness)
            elif tool == 'right_triangle':
                drawRightTriangle(screen, start_pos, mouse_pos, custom_color, thickness)
            elif tool == 'eq_triangle':
                drawEqTriangle(screen, start_pos, mouse_pos, custom_color, thickness)
            elif tool == 'rhombus':
                drawRhombus(screen, start_pos, mouse_pos, custom_color, thickness)

        if is_typing and text_pos:
            font = pygame.font.SysFont(None, 30)
            cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""
            text_surf = font.render(current_text + cursor, True, custom_color)
            screen.blit(text_surf, text_pos)

        drawToolbar(screen, tool, custom_color, thickness)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()