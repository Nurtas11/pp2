import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Verdana", 40)
        self.font_small = pygame.font.SysFont("Verdana", 20)

    def draw_text(self, text, pos, size="large", color=BLACK):
        f = self.font if size == "large" else self.font_small
        img = f.render(text, True, color)
        self.screen.blit(img, pos)

    def draw_button(self, text, rect):
        pygame.draw.rect(self.screen, GRAY, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        text_surf = self.font_small.render(text, True, BLACK)
        self.screen.blit(text_surf, (rect.x + (rect.width - text_surf.get_width())//2, 
                                     rect.y + (rect.height - text_surf.get_height())//2))
        return rect