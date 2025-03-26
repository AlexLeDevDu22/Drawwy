import math
import random
import pygame
from pygame import gfxdraw

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (170, 170, 170)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (65, 105, 225)
LIGHT_BLUE = (119, 181, 254)
VERY_LIGHT_BLUE = (160, 205, 255)
ORANGE = (255, 95, 31)
SOFT_ORANGE = (255, 160, 122)
HIDED_ORANGE = (255, 110, 55, 220)
BEIGE = (245, 222, 179)
DARK_BEIGE = (222, 184, 135)
PASTEL_PINK = (255, 209, 220)
PASTEL_GREEN = (193, 225, 193)
PASTEL_YELLOW = (253, 253, 150)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
LIGHT_BEIGE = (239, 231, 219)
LIGHT_ORANGE = (255, 219, 187)
PINK = (255, 130, 186)
YELLOW = (255, 223, 97)
PURPLE = (130, 94, 196)
LIGHT_PURPLE = (157, 127, 211)

pygame.font.init()
BUTTON_FONT = pygame.font.Font(None, 70)


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

class FloatingObject:
    def __init__(self, x, y, size, color, speed, W):
        self.x = x
        self.y = y
        self.W = W
        self.size = size
        self.color = color
        self.speed = speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.orig_y = y
        self.amplitude = random.uniform(20, 50)
        self.phase = random.uniform(0, 2 * math.pi)

    def update(self):
        self.x += self.speed
        self.phase += 0.02
        self.y = self.orig_y + math.sin(self.phase) * self.amplitude

        if self.x > self.W + 100:
            self.x = -100

    def draw(self, screen):
        # Dessiner un cercle flou
        for i in range(5):
            radius = self.size - i
            alpha = 100 - i * 20
            gfxdraw.filled_circle(
                screen, int(
                    self.x), int(
                    self.y), radius, (*self.color, alpha))
