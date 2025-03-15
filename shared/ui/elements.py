import random
import pygame

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
