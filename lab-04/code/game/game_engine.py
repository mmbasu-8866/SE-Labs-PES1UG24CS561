import json
import os
import time
from collections import deque

import pygame

from game.maze import CELL, generate_maze
from game.player import Player

FPS = 60
BG = (240, 235, 220)
WALL_COLOR = (40, 40, 60)
EXIT_COLOR = (80, 200, 80)
PATH_COLOR = (255, 180, 50)
FOG_COLOR = (15, 15, 20)
BUTTON_COLOR = (54, 90, 140)
BUTTON_HOVER = (72, 118, 176)
COLS, ROWS = 15, 13
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 60
DIFFICULTIES = {
    "easy": (10, 8),
    "medium": (15, 13),
    "hard": (20, 18),
}
LEADERBOARD_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "leaderboard.json")


class GameEngine:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 36, bold=True)
        self.small_font = pygame.font.SysFont("monospace", 16)
        self.current_difficulty = "medium"
        self.state = "menu"
        self.load_leaderboard()
        self.set_difficulty(self.current_difficulty, show_menu=True)

    def set_difficulty(self, difficulty_name, show_menu=False):
        if difficulty_name not in DIFFICULTIES:
            difficulty_name = "medium"
        self.current_difficulty = difficulty_name
        self.cols, self.rows = DIFFICULTIES[difficulty_name]
        global COLS, ROWS, WIDTH, HEIGHT
        COLS, ROWS = self.cols, self.rows
        WIDTH = self.cols * CELL
        HEIGHT = self.rows * CELL + 60
        self.width = WIDTH
        self.height = HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(f"Maze Runner - {difficulty_name.title()}")
        self.reset()
        self.state = "playing"
        if show_menu:
            self.state = "menu"
            self.setup_menu_buttons()

    def load_leaderboard(self):
        try:
            with open(LEADERBOARD_PATH, "r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, list):
                self.leaderboard = sorted(float(v) for v in loaded)
                return
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        self.leaderboard = []

    def save_leaderboard(self):
        with open(LEADERBOARD_PATH, "w", encoding="utf-8") as fh:
            json.dump(self.leaderboard[:5], fh)

    def setup_menu_buttons(self):
        self.menu_buttons = {}
        button_width = 160
        button_height = 54
        start_x = (self.width or 420) // 2 - button_width // 2
        start_y = 120
        for i, (name, (cols, rows)) in enumerate(DIFFICULTIES.items()):
            rect = pygame.Rect(start_x, start_y + i * 90, button_width, button_height)
            self.menu_buttons[name] = rect

    def reset(self):
        self.walls = generate_maze(self.cols, self.rows)
        self.player = Player(0, 0)
        self.exit_rect = pygame.Rect((self.cols - 1) * CELL + 5, (self.rows - 1) * CELL + 5, CELL - 10, CELL - 10)
        self.start_time = time.time()
        self.elapsed = 0
        self.won = False
        self.path = self.compute_shortest_path()
        self.path_toggle = False
        self.show_fog = True

    def compute_shortest_path(self):
        start = (0, 0)
        goal = (self.rows - 1, self.cols - 1)
        queue = deque([start])
        prev = {start: None}

        while queue:
            r, c = queue.popleft()
            if (r, c) == goal:
                break
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in prev and self._can_move(r, c, nr, nc):
                    prev[(nr, nc)] = (r, c)
                    queue.append((nr, nc))

        if goal not in prev:
            return []

        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path

    def _can_move(self, r1, c1, r2, c2):
        if r2 == r1 - 1:
            return not self.walls[r1][c1][0]
        if r2 == r1 + 1:
            return not self.walls[r1][c1][1]
        if c2 == c1 - 1:
            return not self.walls[r1][c1][3]
        if c2 == c1 + 1:
            return not self.walls[r1][c1][2]
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if self.state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for name, rect in self.menu_buttons.items():
                        if rect.collidepoint(event.pos):
                            self.set_difficulty(name)
                            return True
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()
                elif event.key == pygame.K_h:
                    self.path_toggle = not self.path_toggle

        return True

    def update(self):
        if self.state != "playing" or self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.walls, self.rows, self.cols)
        self.elapsed = time.time() - self.start_time

        if self.player.rect.colliderect(self.exit_rect):
            self.won = True
            self.record_leaderboard()

    def record_leaderboard(self):
        if self.elapsed <= 0:
            return
        self.leaderboard.append(self.elapsed)
        self.leaderboard = sorted(float(v) for v in self.leaderboard)[:5]
        self.save_leaderboard()

    def draw_maze(self):
        wall_w = 3
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = c * CELL, r * CELL
                w = self.walls[r][c]
                if w[0]:
                    pygame.draw.line(self.screen, WALL_COLOR, (x, y), (x + CELL, y), wall_w)
                if w[1]:
                    pygame.draw.line(self.screen, WALL_COLOR, (x, y + CELL), (x + CELL, y + CELL), wall_w)
                if w[2]:
                    pygame.draw.line(self.screen, WALL_COLOR, (x + CELL, y), (x + CELL, y + CELL), wall_w)
                if w[3]:
                    pygame.draw.line(self.screen, WALL_COLOR, (x, y), (x, y + CELL), wall_w)

    def draw_path(self):
        if not self.path_toggle or not self.path:
            return
        for r, c in self.path:
            cell_rect = pygame.Rect(c * CELL + 8, r * CELL + 8, CELL - 16, CELL - 16)
            pygame.draw.rect(self.screen, PATH_COLOR, cell_rect, border_radius=6)

    def draw_fog(self):
        if not self.show_fog:
            return
        fog = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 180))
        center_x = int(self.player.rect.centerx)
        center_y = int(self.player.rect.centery)
        radius = CELL * 3
        pygame.draw.circle(fog, (0, 0, 0, 0), (center_x, center_y), radius)
        self.screen.blit(fog, (0, 0))

    def draw_menu(self):
        self.screen.fill((238, 234, 220))
        title = self.big_font.render("Choose a maze difficulty", True, (40, 40, 60))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 30))
        quit_hint = self.font.render("Press Esc to quit", True, (70, 70, 80))
        self.screen.blit(quit_hint, (self.width // 2 - quit_hint.get_width() // 2, 78))

        for name, rect in self.menu_buttons.items():
            color = BUTTON_COLOR
            if rect.collidepoint(pygame.mouse.get_pos()):
                color = BUTTON_HOVER
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            label = self.font.render(name.title(), True, (255, 255, 255))
            self.screen.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
            pygame.display.flip()
            return

        self.screen.fill(BG)
        self.draw_maze()
        self.draw_path()
        self.draw_fog()
        pygame.draw.rect(self.screen, EXIT_COLOR, self.exit_rect, border_radius=4)
        ex_label = self.font.render("EXIT", True, (20, 80, 20))
        self.screen.blit(ex_label, (self.exit_rect.x + 2, self.exit_rect.y + 4))
        self.player.draw(self.screen)

        hud = pygame.Rect(0, self.rows * CELL, self.width, 60)
        pygame.draw.rect(self.screen, (30, 30, 50), hud)
        time_surf = self.small_font.render(
            f"Time: {self.elapsed:.1f}s   H: Hint   R: New Maze   Esc: Quit",
            True,
            (200, 200, 200),
        )
        self.screen.blit(time_surf, (10, self.rows * CELL + 18))

        if self.won:
            overlay = pygame.Surface((self.width, self.rows * CELL), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            self.screen.blit(overlay, (0, 0))
            msg = self.big_font.render(f"Solved in {self.elapsed:.1f}s!", True, (80, 240, 80))
            sub = self.font.render("Press R for a new maze", True, (200, 200, 200))
            self.screen.blit(msg, (self.width // 2 - msg.get_width() // 2, self.rows * CELL // 2 - 30))
            self.screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.rows * CELL // 2 + 20))
            if self.leaderboard:
                title = self.small_font.render("Top 5 completion times", True, (255, 255, 255))
                title_y = self.rows * CELL // 2 + 50
                self.screen.blit(title, (self.width // 2 - title.get_width() // 2, title_y))
                for index, value in enumerate(self.leaderboard[:5], start=1):
                    line = self.small_font.render(f"{index}. {value:.2f}s", True, (255, 255, 255))
                    line_y = title_y + 20 + (index - 1) * 18
                    self.screen.blit(line, (self.width // 2 - line.get_width() // 2, line_y))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
