from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text

import random
import pygame


class Button:
    def __init__(self, x, y, w=None, h=None, text=None,  radius=40,circle=False, text_font=BUTTON_FONT, image=None):
        if not circle:
            self.W, self.H = w, h
            if not w:
                self.W= text_font.size(text)[0]+20
            if not h:
                self.H =text_font.size(text)[1]+20
        else:
            self.W, self.H = radius*2, radius*2
        self.X = (pygame.display.Info().current_w-self.W) // 2 if x=="center" else x
        self.Y = (pygame.display.Info().current_h-self.H) // 2 if y=="center" else y
        self.rect=pygame.Rect(self.X, self.Y, self.W, self.H)
        self.offsets = 5
        self.text = text
        self.text_font = text_font
        self.hover=False
        self.radius = radius
        self.image=image
        self.circle=circle

    def draw(self, screen):
        # ombre
        pygame.draw.rect(screen, DARK_BEIGE if not self.hover else GRAY, 
                    (self.X + self.offsets, self.Y + self.offsets, self.W, self.H), 
                    border_radius=self.radius)
        
        # bouton
        self.rect=pygame.Rect(self.X, self.Y, self.W, self.H)
        pygame.draw.rect(screen, 
                        SOFT_ORANGE if self.hover else ORANGE, 
                        (self.X, self.Y, self.W, self.H), 
                        border_radius=self.radius)
        
        if self.text:
            # texte
            draw_text(self.text, self.text_font, BLACK, screen, 
                    self.X + self.W // 2, 
                    self.Y + self.H // 2 - (3 if self.hover else 0))
        else:
            image = pygame.image.load(self.image)
            image = pygame.transform.smoothscale(image, (self.W+20, self.H+20))
            screen.blit(image, ((self.X-self.W//2), (self.Y-self.H)//2))
        
    def check_hover(self, pos):
        self.hover=self.rect.collidepoint(pos)
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
