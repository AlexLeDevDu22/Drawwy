import math
import random
from pygame import gfxdraw

import pygame
import math
import random
from shared.ui.common_ui import *

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


class Confetti:
    def __init__(self):
        self.particles = []

    def add_particles(
        self, x, y, color, count=20, speed_range=(
            1, 3), size_range=(
            2, 5), life_range=(
                30, 60)):
        """Ajoute plusieurs particules à partir d'une position donnée"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            size = random.uniform(*size_range)
            life = random.uniform(*life_range)

            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'life': life,
                'max_life': life,
                'color': color,
                'gravity': random.uniform(0.02, 0.08)
            })

    def add_confetti(self, x, y, count=1):
        """Ajoute des confettis colorés"""
        colors = [GOLD, BLUE, PINK, GREEN, YELLOW]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            size = random.uniform(3, 8)
            life = random.uniform(60, 120)
            rotation_speed = random.uniform(-5, 5)

            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'life': life,
                'max_life': life,
                'color': random.choice(colors),
                'gravity': random.uniform(0.02, 0.08),
                'type': 'confetti',
                'rotation': random.uniform(0, 360),
                'rotation_speed': rotation_speed
            })

    def update(self):
        """Met à jour toutes les particules"""
        for particle in self.particles:
            # Mise à jour de la position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            # Appliquer la gravité
            particle['vy'] += particle['gravity']

            # Réduire la durée de vie
            particle['life'] -= 1

            # Mettre à jour la rotation pour les confettis
            if 'type' in particle and particle['type'] == 'confetti':
                particle['rotation'] += particle['rotation_speed']

        # Supprimer les particules expirées
        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self, surface):
        """Dessine toutes les particules actives"""
        for particle in self.particles:
            # Calculer l'opacité basée sur la durée de vie restante
            alpha = int(255 * (particle['life'] / particle['max_life']))

            if 'type' in particle and particle['type'] == 'confetti':
                # Dessiner un confetti (rectangle avec rotation)
                rect_surface = pygame.Surface(
                    (particle['size'] * 2, particle['size']), pygame.SRCALPHA)
                pygame.draw.rect(
                    rect_surface,
                    (*particle['color'], alpha),
                    (0, 0, particle['size'] * 2, particle['size'])
                )

                # Rotation du confetti
                rotated_surface = pygame.transform.rotate(rect_surface, particle['rotation'])
                rotated_rect = rotated_surface.get_rect(center=(particle['x'], particle['y']))
                surface.blit(rotated_surface, rotated_rect)

            else:
                # Utiliser une surface temporaire pour l'alpha
                temp_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                temp_surface.fill((0, 0, 0, 0))  # Rendre la surface transparente 
                color = tuple(map(int, particle['color'])) + (alpha,)
                gfxdraw.filled_circle(
                    temp_surface,
                    int(particle['size']),  # Convertir en entier
                    int(particle['size']),  # Convertir en entier
                    int(particle['size']),  # Déjà converti, c'est bien
                    (*particle['color'], alpha)
                )
                surface.blit(temp_surface, (int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))
