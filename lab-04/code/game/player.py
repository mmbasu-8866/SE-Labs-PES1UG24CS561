import pygame
from game.maze import CELL

SPEED = 3

class Player:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        x = c * CELL + CELL // 2
        y = r * CELL + CELL // 2
        self.rect = pygame.Rect(x - 10, y - 10, 20, 20)
        self.color = (60, 120, 220)

    def move(self, keys, walls, rows, cols):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = SPEED

        new_rect = self.rect.move(dx, 0)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

        new_rect = self.rect.move(0, dy)
        if not self._hits_wall(new_rect, walls, rows, cols):
            self.rect = new_rect

    def _hits_wall(self, rect, walls, rows, cols):
        sample_points = [
            (rect.left + 2, rect.top + 2),
            (rect.right - 3, rect.top + 2),
            (rect.left + 2, rect.bottom - 3),
            (rect.right - 3, rect.bottom - 3),
        ]

        for px, py in sample_points:
            if px < 0 or py < 0 or px >= cols * CELL or py >= rows * CELL:
                return True

            r = py // CELL
            c = px // CELL
            if r < 0 or r >= rows or c < 0 or c >= cols:
                return True

            x_in_cell = px - c * CELL
            y_in_cell = py - r * CELL
            boundary_margin = 4

            if x_in_cell <= boundary_margin and walls[r][c][3]:
                return True
            if x_in_cell >= CELL - boundary_margin and walls[r][c][2]:
                return True
            if y_in_cell <= boundary_margin and walls[r][c][0]:
                return True
            if y_in_cell >= CELL - boundary_margin and walls[r][c][1]:
                return True

        return False

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
