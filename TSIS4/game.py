import random
import pygame

from db import get_personal_best
from ui import draw_text, FONT, SMALL_FONT, WHITE, BLACK

# Display and grid layout constants
WIDTH = 700
HEIGHT = 700
TOP_PANEL = 80

CELL_SIZE = 20
COLS = WIDTH // CELL_SIZE
ROWS = (HEIGHT - TOP_PANEL) // CELL_SIZE

# Rules for movement and item timing
BASE_SPEED = 8
FOODS_FOR_NEXT_LEVEL = 4

NORMAL_FOOD_LIFETIME = 7000
POWERUP_LIFETIME = 8000
POWERUP_DURATION = 5000

class SnakeGame:
    def __init__(self, screen, clock, username, settings):
        # Localize engine and user data
        self.screen = screen
        self.clock = clock
        self.username = username
        self.settings = settings

        # Apply visual preferences from settings
        self.snake_color = tuple(settings["snake_color"])
        self.grid_enabled = settings["grid"]

        # Fetch record from DB; default to 0 if connection fails
        try:
            self.personal_best = get_personal_best(username)
        except Exception:
            self.personal_best = 0

        # Initial snake shape (3 segments) and movement direction
        self.snake = [(8, 8), (7, 8), (6, 8)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

        # Leveling and scoring tracking
        self.score = 0
        self.level = 1
        self.food_eaten_on_level = 0
        self.speed = BASE_SPEED

        # Lists/Objects for items on the map
        self.obstacles = []
        self.normal_food = None
        self.poison_food = None
        self.powerup = None

        # Buff/Debuff state tracking
        self.active_powerup = None
        self.powerup_end_time = 0
        self.shield = False

        self.game_over = False

        # Populate map for the first time
        self.spawn_normal_food()
        self.spawn_poison_food()

    def grid_to_pixel(self, pos):
        # Convert grid (x, y) to screen pixels, accounting for HUD height
        x, y = pos
        return x * CELL_SIZE, TOP_PANEL + y * CELL_SIZE

    def is_inside(self, pos):
        # Boundary check for the playable area
        x, y = pos
        return 0 <= x < COLS and 0 <= y < ROWS

    def occupied_cells(self):
        # Returns a set of all coordinates currently holding an object
        cells = set(self.snake)
        cells.update(self.obstacles)

        if self.normal_food:
            cells.add(self.normal_food["pos"])

        if self.poison_food:
            cells.add(self.poison_food["pos"])

        if self.powerup:
            cells.add(self.powerup["pos"])

        return cells

    def random_empty_cell(self):
        # Search for a spot that doesn't overlap with anything
        occupied = self.occupied_cells()

        while True:
            pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))

            if pos not in occupied:
                return pos

    def spawn_normal_food(self):
        # Create food with different point values and colors
        value = random.choice([1, 1, 1, 2, 2, 3, 5])
        colors = {
            1: (220, 0, 0),
            2: (255, 140, 0),
            3: (230, 230, 0),
            5: (150, 0, 220)
        }

        self.normal_food = {
            "pos": self.random_empty_cell(),
            "value": value,
            "color": colors[value],
            "spawn_time": pygame.time.get_ticks()
        }

    def spawn_poison_food(self):
        # Half the time, spawn a dangerous red block
        if random.random() < 0.55:
            self.poison_food = {
                "pos": self.random_empty_cell(),
                "spawn_time": pygame.time.get_ticks()
            }
        else:
            self.poison_food = None

    def spawn_powerup(self):
        # Low chance to drop a special utility item if one isn't already out
        if self.powerup is not None:
            return

        if random.random() < 0.015:
            self.powerup = {
                "pos": self.random_empty_cell(),
                "type": random.choice(["speed", "slow", "shield"]),
                "spawn_time": pygame.time.get_ticks()
            }

    def create_obstacles_for_level(self):
        # Build walls for higher difficulty levels
        if self.level < 3:
            return

        self.obstacles.clear()

        count = min(8 + self.level * 2, 28)
        head = self.snake[0]

        # Ensure walls don't spawn right on top of the snake's head
        safe_area = {
            head,
            (head[0] + 1, head[1]),
            (head[0] - 1, head[1]),
            (head[0], head[1] + 1),
            (head[0], head[1] - 1)
        }

        attempts = 0

        while len(self.obstacles) < count and attempts < 500:
            attempts += 1
            pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))

            if pos in self.snake or pos in safe_area or pos in self.obstacles:
                continue

            self.obstacles.append(pos)

    def change_level(self):
        # Progress difficulty and reset level-specific counters
        self.level += 1
        self.food_eaten_on_level = 0
        self.speed += 1
        self.create_obstacles_for_level()

        self.spawn_normal_food()
        self.spawn_poison_food()
        self.powerup = None

    def activate_powerup(self, power_type):
        # Setup duration and effects for the collected power-up
        now = pygame.time.get_ticks()
        self.active_powerup = power_type

        if power_type == "speed" or power_type == "slow":
            self.powerup_end_time = now + POWERUP_DURATION
        elif power_type == "shield":
            self.shield = True
            self.powerup_end_time = 0

    def current_speed(self):
        # Calculate final speed based on level and active modifiers
        if self.active_powerup == "speed":
            return self.speed + 4
        if self.active_powerup == "slow":
            return max(4, self.speed - 4)
        return self.speed

    def update_powerup_time(self):
        # Check if the speed/slow timer has run out
        now = pygame.time.get_ticks()
        if self.active_powerup in ["speed", "slow"]:
            if now >= self.powerup_end_time:
                self.active_powerup = None
                self.powerup_end_time = 0

    def use_shield_or_die(self):
        # Try to use the extra life; if not available, kill the session
        if self.shield:
            self.shield = False
            self.active_powerup = None
            return False

        self.game_over = True
        return True

    def handle_input(self, event):
        # Map keys to direction; prevents reversing into own neck
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_UP or event.key == pygame.K_w:
            if self.direction != (0, 1):
                self.next_direction = (0, -1)
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            if self.direction != (0, -1):
                self.next_direction = (0, 1)
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            if self.direction != (1, 0):
                self.next_direction = (-1, 0)
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            if self.direction != (-1, 0):
                self.next_direction = (1, 0)

    def move(self):
        # Main game logic loop
        self.update_powerup_time()
        now = pygame.time.get_ticks()

        # Refresh items if they have expired
        if self.normal_food and now - self.normal_food["spawn_time"] > NORMAL_FOOD_LIFETIME:
            self.spawn_normal_food()
        if self.poison_food and now - self.poison_food["spawn_time"] > NORMAL_FOOD_LIFETIME:
            self.spawn_poison_food()
        if self.powerup and now - self.powerup["spawn_time"] > POWERUP_LIFETIME:
            self.powerup = None

        self.spawn_powerup()
        self.direction = self.next_direction

        # Determine next step for the head
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check collisions (Walls, Body, Walls)
        if not self.is_inside(new_head) or new_head in self.snake or new_head in self.obstacles:
            if self.use_shield_or_die():
                return
            new_head = self.snake[0]

        # Add new head to list
        self.snake.insert(0, new_head)

        ate_normal = self.normal_food and new_head == self.normal_food["pos"]
        ate_poison = self.poison_food and new_head == self.poison_food["pos"]
        ate_powerup = self.powerup and new_head == self.powerup["pos"]

        if ate_normal:
            # Handle scoring and growth
            self.score += self.normal_food["value"] * 10
            self.food_eaten_on_level += 1
            self.spawn_normal_food()
            if self.food_eaten_on_level >= FOODS_FOR_NEXT_LEVEL:
                self.change_level()
        elif ate_poison:
            # Shorten the snake significantly
            self.poison_food = None
            for _ in range(3):
                if self.snake:
                    self.snake.pop()
            if len(self.snake) <= 1:
                self.game_over = True
                return
            self.spawn_poison_food()
        elif ate_powerup:
            # Apply effect and pop tail
            self.activate_powerup(self.powerup["type"])
            self.powerup = None
            self.snake.pop()
        else:
            # Standard movement: remove tail as head advances
            self.snake.pop()

    def draw_grid(self):
        # Draw light grey lines if option is enabled
        if not self.grid_enabled:
            return
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (220, 220, 220), (x, TOP_PANEL), (x, HEIGHT))
        for y in range(TOP_PANEL, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (220, 220, 220), (0, y), (WIDTH, y))

    def draw_cell(self, pos, color):
        # Helper to draw a filled square with a border
        x, y = self.grid_to_pixel(pos)
        rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_hud(self):
        # Render the top statistics panel
        pygame.draw.rect(self.screen, (245, 245, 245), (0, 0, WIDTH, TOP_PANEL))
        pygame.draw.line(self.screen, BLACK, (0, TOP_PANEL), (WIDTH, TOP_PANEL), 2)

        draw_text(self.screen, f"Player: {self.username}", 10, 8)
        draw_text(self.screen, f"Score: {self.score}", 10, 40)
        draw_text(self.screen, f"Level: {self.level}", 220, 8)
        draw_text(self.screen, f"Speed: {self.current_speed()}", 220, 40)
        draw_text(self.screen, f"Best: {self.personal_best}", 390, 8)

        # Show current power-up status and timers
        if self.active_powerup in ["speed", "slow"]:
            remaining = max(0, (self.powerup_end_time - pygame.time.get_ticks()) // 1000)
            power_text = f"Power: {self.active_powerup} {remaining}s"
        elif self.shield:
            power_text = "Power: shield"
        else:
            power_text = "Power: none"
        draw_text(self.screen, power_text, 390, 40)

    def draw(self):
        # Render everything on the screen
        self.screen.fill((250, 250, 250))
        self.draw_hud()
        self.draw_grid()

        for block in self.obstacles:
            self.draw_cell(block, (90, 90, 90))

        if self.normal_food:
            self.draw_cell(self.normal_food["pos"], self.normal_food["color"])
            x, y = self.grid_to_pixel(self.normal_food["pos"])
            draw_text(self.screen, self.normal_food["value"], x + 5, y, BLACK, SMALL_FONT)

        if self.poison_food:
            self.draw_cell(self.poison_food["pos"], (100, 0, 0))
            x, y = self.grid_to_pixel(self.poison_food["pos"])
            draw_text(self.screen, "P", x + 5, y, WHITE, SMALL_FONT)

        if self.powerup:
            colors = {"speed": (0, 200, 255), "slow": (255, 180, 0), "shield": (120, 120, 255)}
            letters = {"speed": "B", "slow": "S", "shield": "H"}
            self.draw_cell(self.powerup["pos"], colors[self.powerup["type"]])
            x, y = self.grid_to_pixel(self.powerup["pos"])
            draw_text(self.screen, letters[self.powerup["type"]], x + 4, y, BLACK, SMALL_FONT)

        for i, segment in enumerate(self.snake):
            self.draw_cell(segment, (0, 120, 0) if i == 0 else self.snake_color)

    def run(self):
        # Entry point for the game state
        while not self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit", self.score, self.level
                self.handle_input(event)

            self.move()
            self.draw()
            pygame.display.flip()
            self.clock.tick(self.current_speed())

        return "game_over", self.score, self.level