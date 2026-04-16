import pygame
import math
import datetime

class MickeysClock:
    def __init__(self, screen_width=800, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2

       

        # hand size
        self.HAND_IMG_W = 500
        self.HAND_IMG_H = 375  

        # angle callib
        self.HAND_BASE_ANGLE = 0  

        # pivot points
        self.HAND_PIVOT_FX = 0.5       
        self.HAND_PIVOT_FY = 0.5       

        # clock and body cal
        self.CLOCK_SIZE = 520
        self.BODY_IMG_W = 500
        self.BODY_IMG_H = 375
        self.BODY_OFFSET_X = 0
        self.BODY_OFFSET_Y = -20    

        
        self.clock_surf = None
        self.body_surf  = None
        self.hand_surf  = None

    def load_images(self):
        try:
            raw_clock = pygame.image.load("images/clock.png").convert_alpha()
            raw_body  = pygame.image.load("images/body.png").convert_alpha()
            raw_hand  = pygame.image.load("images/hands.png").convert_alpha()
        except pygame.error as e:
            raise SystemExit(f"error: {e}")

        self.clock_surf = pygame.transform.smoothscale(raw_clock, (self.CLOCK_SIZE, self.CLOCK_SIZE))
        self.body_surf = pygame.transform.smoothscale(raw_body, (self.BODY_IMG_W, self.BODY_IMG_H))
        self.hand_surf = pygame.transform.smoothscale(raw_hand, (self.HAND_IMG_W, self.HAND_IMG_H))

    def _rotated_hand(self, time_angle_cw_deg):
        
        src = self.hand_surf 

        # rotation calc (pygame uses counter clockwise, we need clockwise)
        total_ccw = self.HAND_BASE_ANGLE - time_angle_cw_deg
        rotated = pygame.transform.rotozoom(src, total_ccw, 1.0)

        # pivot calculation
        pw, ph = self.HAND_IMG_W, self.HAND_IMG_H
        dx = self.HAND_PIVOT_FX * pw - pw / 2
        dy = self.HAND_PIVOT_FY * ph - ph / 2

        rad = math.radians(total_ccw)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rdx = dx * cos_a - dy * sin_a
        rdy = dx * sin_a + dy * cos_a

        rot_cx, rot_cy = rotated.get_width() / 2, rotated.get_height() / 2
        piv_rx, piv_ry = rot_cx + rdx, rot_cy + rdy

        # this is used to keep pivot at center
        bx = self.center_x - piv_rx
        by = self.center_y - piv_ry

        return rotated, (bx, by)

    @staticmethod #used to define method inside a class that does not need access to the class
    def _clock_angle(value, total):
        return (value / total) * 360.0

    def draw(self, surface):
        now = datetime.datetime.now()
        
        #time
        minutes = now.minute
        seconds = now.second

        min_angle = self._clock_angle(minutes + seconds / 60.0, 60)
        sec_angle = self._clock_angle(seconds, 60)

        cx, cy = self.center_x, self.center_y

        # clock face
        surface.blit(self.clock_surf, self.clock_surf.get_rect(center=(cx, cy)))

        #body
        bx = cx + self.BODY_OFFSET_X - self.BODY_IMG_W // 2
        by = cy + self.BODY_OFFSET_Y - self.BODY_IMG_H // 2
        surface.blit(self.body_surf, (bx, by))

        # minute hand
        ms, mp = self._rotated_hand(min_angle)
        surface.blit(ms, mp)

        # seconds hand
        ss, sp = self._rotated_hand(sec_angle)
        surface.blit(ss, sp)