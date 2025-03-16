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
VERY_LIGHT_BLUE= (160, 205, 255)
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

class Button:
    def __init__(self, x, y, w=None, h=None, text=None, radius=40, circle=False, text_font=BUTTON_FONT, image=None, active=True):
        if not circle:
            self.W = w if w else text_font.size(text)[0] + 32
            self.H = h if h else text_font.size(text)[1] + 22
        else:
            self.W, self.H = radius * 2, radius * 2
        
        self.X = (pygame.display.Info().current_w - self.W) // 2 if x == "center" else x
        self.Y = (pygame.display.Info().current_h - self.H) // 2 if y == "center" else y
        self.rect = pygame.Rect(self.X, self.Y, self.W, self.H)
        self.offsets = 5
        self.text = text
        self.text_font = text_font
        self.hover = False
        self.radius = radius
        self.image = image
        self.circle = circle
        self.active = active
        self.disabled_color = HIDED_ORANGE  # Gris pour les boutons désactivés
        self.shadow_offset = 5

    def draw(self, screen):
        color = SOFT_ORANGE if self.hover else (ORANGE if self.active else self.disabled_color)
        shadow_color = DARK_BEIGE if self.active else (100, 100, 100)
        text_color = BLACK if self.active else (120, 120, 120)

        # Ombre
        pygame.draw.rect(screen, shadow_color, (self.X + self.shadow_offset, self.Y + self.shadow_offset, self.W, self.H), border_radius=self.radius)
        
        # Bouton principal
        pygame.draw.rect(screen, color, (self.X, self.Y, self.W, self.H), border_radius=self.radius)
        
        if self.text:
            # Texte
            draw_text(self.text, self.text_font, text_color, screen, self.X + self.W // 2, self.Y + self.H // 2 - (2 if self.hover else 0))
        elif self.image:
            # Image
            image = pygame.image.load(self.image)
            image = pygame.transform.smoothscale(image, (int(self.W * 0.7), int(self.H * 0.7)))
            image.set_alpha(255 if self.active else 180)  # Réduction d'opacité si désactivé
            screen.blit(image, (self.X + self.W * 0.15, self.Y + self.H * 0.15))

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos) and self.active
        return self.hover


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
            gfxdraw.filled_circle(screen, int(self.x), int(self.y), radius, (*self.color, alpha))
