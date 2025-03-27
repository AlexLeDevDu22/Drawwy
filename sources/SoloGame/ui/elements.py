import math
import random
from pygame import gfxdraw

import pygame
import math
import random
from shared.ui.common_ui import *


class FloatingObject:
    def __init__(self, x, y, size, color, speed, W):
        """
        Initialize a FloatingObject with the given parameters.

        :param x: The x-coordinate of the particle.
        :type x: int or float
        :param y: The y-coordinate of the particle.
        :type y: int or float
        :param size: The size of the particle.
        :type size: int or float
        :param color: The color of the particle.
        :type color: tuple
        :param speed: The speed of the particle.
        :type speed: int or float
        :param W: The width of the screen.
        :type W: int
        """
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
        """
        Update the position of the floating object.

        This method updates the position of the floating object using a sine
        wave with a random amplitude and phase. The position is updated by
        adding the speed to the current x-coordinate and computing the new
        y-coordinate using the sine wave. If the x-coordinate exceeds the width
        of the screen plus 100, the x-coordinate is reset to -100.
        """
        self.x += self.speed
        self.phase += 0.02
        self.y = self.orig_y + math.sin(self.phase) * self.amplitude

        if self.x > self.W + 100:
            self.x = -100

    def draw(self, screen):
        """
        Draw a blurred circle.

        This method draws a blurred circle of decreasing radius
        and increasing transparency around the particle's position.
        The color of the particle is used to draw the circle.
        """
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
        """
        Add multiple particles at a given position.

        This method creates a specified number of particles, each with random
        attributes such as angle, speed, size, and life span. The particles are
        assigned a velocity based on their angle and speed, and appended to the
        particle list with their initial position, color, and a randomly assigned
        gravity.

        :param x: The x-coordinate of the starting position.
        :type x: float
        :param y: The y-coordinate of the starting position.
        :type y: float
        :param color: The color of the particles.
        :type color: tuple
        :param count: The number of particles to generate. Defaults to 20.
        :type count: int
        :param speed_range: A tuple representing the min and max speed. Defaults to (1, 3).
        :type speed_range: tuple
        :param size_range: A tuple representing the min and max size. Defaults to (2, 5).
        :type size_range: tuple
        :param life_range: A tuple representing the min and max life span. Defaults to (30, 60).
        :type life_range: tuple
        """

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
        """
        Add confetti particles to the particle system.

        This method generates particles with different angles, speeds, sizes, life
        spans, and colors. The particles are assigned a velocity based on their
        angle and speed, and appended to the particle list with their initial
        position, color, and a randomly assigned gravity and rotation speed.

        :param x: The x-coordinate of the starting position.
        :type x: float
        :param y: The y-coordinate of the starting position.
        :type y: float
        :param count: The number of particles to generate. Defaults to 1.
        :type count: int
        """
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
        """
        Update the particles in the system.

        This method updates the position, velocity, and life span of each particle
        in the system. It applies gravity to the particles and reduces their life
        span. It also updates the rotation of confetti particles. Finally, it
        removes particles whose life span has expired.

        :return: None
        """
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
        """
        Draw all the particles in the system onto the given surface.

        This method iterates over all the particles in the system and draws them
        onto the given surface. It takes into account the particle's position,
        size, color, alpha value, gravity, and type (confetti or not). For confetti
        particles, it rotates the drawn rectangle to match the particle's rotation.

        :param surface: The surface on which to draw the particles.
        :type surface: pygame.Surface
        :return: None
        """
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
                rotated_surface = pygame.transform.rotate(
                    rect_surface, particle['rotation'])
                rotated_rect = rotated_surface.get_rect(
                    center=(particle['x'], particle['y']))
                surface.blit(rotated_surface, rotated_rect)

            else:
                # Utiliser une surface temporaire pour l'alpha
                temp_surface = pygame.Surface(
                    (particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                # Rendre la surface transparente
                temp_surface.fill((0, 0, 0, 0))
                color = tuple(map(int, particle['color'])) + (alpha,)
                gfxdraw.filled_circle(
                    temp_surface,
                    int(particle['size']),  # Convertir en entier
                    int(particle['size']),  # Convertir en entier
                    int(particle['size']),  # Déjà converti, c'est bien
                    (*particle['color'], alpha)
                )
                surface.blit(temp_surface,
                             (int(particle['x'] - particle['size']),
                              int(particle['y'] - particle['size'])))
