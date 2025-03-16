from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text

import random
import pygame


class Button:
    def __init__(self, x, y, w=None, h=None, text=None, radius=40, circle=False, text_font=BUTTON_FONT, image=None, active=True):
        if not circle:
            self.W = w if w else text_font.size(text)[0] + 16
            self.H = h if h else text_font.size(text)[1] + 40
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

# Classe pour les effets de particules
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(-3, -1)
        self.lifetime = random.randint(30, 90)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.05)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class ColorPicker:
    def __init__(self, x, y, width, height, color_steps=30, dark_steps=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_steps = color_steps  # Beaucoup plus de teintes
        self.dark_steps = dark_steps  # Plus de niveaux d'assombrissement
        self.colors = self.generate_colors()
        self.selected_color = None
        self.selected_pos = None

    def generate_colors(self):
        colors = []
        for j in range(self.dark_steps):
            row = []
            for i in range(self.color_steps):
                hue = i / self.color_steps * 360  # Teinte (HSV)
                brightness = 1 - (j / (self.dark_steps - 1))  # Assombrissement progressif
                color = pygame.Color(0)
                color.hsva = (hue, 100, brightness * 100)
                row.append(color)
            colors.append(row)
        return colors

    def draw(self, surface):
        step_w = self.rect.width // self.color_steps
        step_h = self.rect.height // self.dark_steps

        # Dessiner la grille de couleurs
        for j, row in enumerate(self.colors):
            for i, color in enumerate(row):
                color_rect = pygame.Rect(
                    self.rect.x + i * step_w, 
                    self.rect.y + j * step_h, 
                    step_w, 
                    step_h
                )
                pygame.draw.rect(surface, color, color_rect)

        # Indiquer la couleur sélectionnée
        if self.selected_color and self.selected_pos:
            px, py = self.selected_pos
            pygame.draw.rect(surface, WHITE, (px, py, step_w, step_h), 3)

    def get_color_at(self, pos):
        x, y = pos
        if self.rect.collidepoint(x, y):
            step_w = self.rect.width // self.color_steps
            step_h = self.rect.height // self.dark_steps
            i = (x - self.rect.x) // step_w
            j = (y - self.rect.y) // step_h
            try: self.selected_color = self.colors[j][i]
            except IndexError: return None
            self.selected_pos = (self.rect.x + i * step_w, self.rect.y + j * step_h)
            return (self.selected_color.r, self.selected_color.g, self.selected_color.b)
        return None