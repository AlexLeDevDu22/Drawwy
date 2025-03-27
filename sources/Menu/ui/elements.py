import random
import pygame
import math

# Classe pour les éléments de dessin décoratifs


class BackgroundElement:
    def __init__(self, x, y):
        """
        Initialisation de l'objet BackgroundElement.

        :param x: La position x de l'élément
        :param y: La position y de l'élément
        :type x: int
        :type y: int
        """
        self.x = x
        self.y = y
        self.type = random.choice(["flower", "star", "heart", "cloud"])
        self.color = random.choice(
            [(255, 102, 102), (255, 204, 102), (102, 204, 255), (153, 255, 153), (255, 153, 255)])
        self.size = random.randint(20, 50)
        self.title_scale = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.3, 0.5)
        self.title_scale_change = random.uniform(-0.01, 0.01)
        # Store initial parameters for smooth drawing
        self.initial_title_scale = self.title_scale

    def update(self):
        """
        Met à jour la position de l'élément en fonction de sa vitesse et de son angle actuel.

        La position est mise à jour en fonction de la formule suivante:
        - La position x est augmentée de sinus de l'angle actuel, multiplié par la vitesse.
        - La position y est augmentée de cosinus de l'angle actuel, multiplié par la vitesse.
        - L'angle actuel est mis à jour en ajoutant l'angle de changement.
        """
        self.title_scale += self.title_scale_change
        self.x += math.sin(self.title_scale) * self.speed
        self.y += math.cos(self.title_scale) * self.speed

    def draw(self, surface):
        """
        Dessine l'élément sur la surface donnée.

        La méthode draw choisit la méthode appropriée pour dessiner l'élément en fonction de son type.
        Les méthodes de dessin sont:
        - draw_flower pour les fleurs
        - draw_star pour les étoiles
        - draw_heart pour les c?urs
        - draw_cloud pour les nuages

        :param surface: La surface sur laquelle dessiner l'élément
        :type surface: pygame.Surface
        """
        if self.type == "flower":
            self.draw_flower(surface)
        elif self.type == "star":
            self.draw_star(surface)
        elif self.type == "heart":
            self.draw_heart(surface)
        elif self.type == "cloud":
            self.draw_cloud(surface)

    def draw_flower(self, surface):
        """
        Dessine une fleur sur la surface donnée.

        La fleur est représentée par 5 pétales (cercles) disposées de manière régulière
        autour d'un centre. Les pétales sont de la même couleur que l'élément.
        Un cercle jaune est dessiné au centre de la fleur.
        Un cercle noir est dessiné en contour de chaque pétale et du cercle central.

        :param surface: La surface sur laquelle dessiner la fleur
        :type surface: pygame.Surface
        """
        center = (int(self.x), int(self.y))
        petal_distance = self.size // 2.5
        # Remove random trembling by using fixed title_scales
        for title_scale in range(0, 360, 72):
            rad = math.radians(title_scale)
            petal_x = center[0] + int(math.cos(rad) * petal_distance)
            petal_y = center[1] + int(math.sin(rad) * petal_distance)
            pygame.draw.circle(
                surface, self.color, (petal_x, petal_y), self.size // 3)
            pygame.draw.circle(
                surface, (0, 0, 0), (petal_x, petal_y), self.size // 3, 2)
        pygame.draw.circle(surface, (255, 255, 0), center, self.size // 4)
        pygame.draw.circle(surface, (0, 0, 0), center, self.size // 4, 2)

    def draw_star(self, surface):
        """
        Dessine une étoile sur la surface donnée.

        L'étoile est représentée par 10 points disposés de manière régulière
        autour d'un centre. Les points sont de la même couleur que l'élément.
        Un contour noir est dessiné en contour de l'étoile.

        :param surface: La surface sur laquelle dessiner l'étoile
        :type surface: pygame.Surface
        """
        points = []
        # Remove random trembling by using fixed title_scales
        for i in range(10):
            title_scale = math.pi / 5 * i
            radius = self.size if i % 2 == 0 else self.size // 2
            x = self.x + math.cos(title_scale) * radius
            y = self.y + math.sin(title_scale) * radius
            points.append((x, y))
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 3)

    def draw_heart(self, surface):
        # Heart shape parameters
        """
        Dessine un coeur sur la surface donnée.

        Le coeur est représenté par des équations paramétriques pour une forme plus lisse.
        Les points sont de la même couleur que l'élément.
        Un contour noir est dessiné en contour du coeur.

        :param surface: La surface sur laquelle dessiner le coeur
        :type surface: pygame.Surface
        """
        size = self.size
        # Create a list of points for the heart shape
        points = []
        for title_scale in range(0, 360, 5):
            rad = math.radians(title_scale)
            # Heart parametric equations for smoother shape
            x = self.x + 16 * size / 40 * math.sin(rad) ** 3
            y = self.y - (13 * size / 40 * math.cos(rad) - 5 * size / 40 * math.cos(
                2 * rad) - 2 * size / 40 * math.cos(3 * rad) - size / 40 * math.cos(4 * rad))
            points.append((x, y))

        # Fill heart shape
        pygame.draw.polygon(surface, self.color, points)
        # Draw outline
        pygame.draw.polygon(surface, (0, 0, 0), points, 2)

    def draw_cloud(self, surface):
        """
        Dessine un nuage sur la surface donnée.

        Le nuage est représenté par un cercle central plus large, ainsi que 5 cercles
        supplémentaires pour former la forme de nuage. Les cercles sont de la même couleur
        que l'élément. Un contour noir est dessiné en contour du nuage.

        :param surface: La surface sur laquelle dessiner le nuage
        :type surface: pygame.Surface
        """
        # Cloud base parameters
        cloud_radius = self.size // 2.5
        small_radius = cloud_radius * 0.8

        # Main cloud body (larger central circle)
        center = (int(self.x), int(self.y))
        pygame.draw.circle(surface, self.color, center, cloud_radius)

        # Additional circles to form cloud shape
        offsets = [
            (-cloud_radius * 0.8, -cloud_radius * 0.3),  # top left
            (cloud_radius * 0.8, -cloud_radius * 0.3),   # top right
            (-cloud_radius * 1.2, cloud_radius * 0.2),   # middle left
            (cloud_radius * 1.2, cloud_radius * 0.2),    # middle right
            (0, -cloud_radius * 0.7),                  # top middle
        ]

        # Draw additional circles
        for offset in offsets:
            pos = (int(center[0] + offset[0]), int(center[1] + offset[1]))
            pygame.draw.circle(surface, self.color, pos, small_radius)

        # Draw outline to join all circles together
        outline_points = []
        steps = 36
        for i in range(steps):
            title_scale = 2 * math.pi * i / steps

            # Find furthest point at this title_scale
            max_dist = cloud_radius
            max_x, max_y = center[0] + math.cos(
                title_scale) * cloud_radius, center[1] + math.sin(title_scale) * cloud_radius

            for offset in offsets:
                pos = (center[0] + offset[0], center[1] + offset[1])
                # Distance from this circle edge to center
                edge_x = pos[0] + math.cos(title_scale) * small_radius
                edge_y = pos[1] + math.sin(title_scale) * small_radius

                # Distance from center of main cloud
                dist_from_center = math.sqrt(
                    (edge_x - center[0])**2 + (edge_y - center[1])**2)

                if dist_from_center > max_dist:
                    max_dist = dist_from_center
                    max_x, max_y = edge_x, edge_y

            outline_points.append((max_x, max_y))

        # Draw cloud outline
        pygame.draw.polygon(surface, self.color, outline_points)
        pygame.draw.polygon(surface, (0, 0, 0), outline_points, 2)
