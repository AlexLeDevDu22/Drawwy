import math
import random
from pygame import gfxdraw


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
