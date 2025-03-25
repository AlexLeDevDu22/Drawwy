from shared.ui.common_ui import *
from shared.utils.data_manager import *
from SoloGame.ui.elements import Confetti

import pygame
import math
import random

num_stars = 0
for theme in SOLO_THEMES:
    for image in theme["images"]:
        num_stars += image["stars"]

class PopupAnimation:
    def __init__(self,screen, W,H):
        self.screen = screen
        self.popup_width, self.popup_height = 600, 400
        self.popup_x = (W - self.popup_width) // 2
        self.popup_y = -self.popup_height  # Commencer hors écran
        self.target_y = (H - self.popup_height) // 2

        self.started = False

        # Animation de transition
        self.animation_speed = 5
        self.animation_done = False
        self.animation_progress = 0

        # Animation des étoiles
        # Pourcentage de remplissage de chaque étoile
        self.stars_fill = [0, 0, 0]
        self.star_animation_speed = 2
        self.stars_filled = False
        self.star_jump = [0, 0, 0]
        self.star_rotation = [0, 0, 0]

        # Système de particules
        self.particles = Confetti()
        self.particle_timer = 0
        self.shine_angle = 0

        # Flags pour les événements d'animation
        self.entry_particles_created = False
        self.star_particles_created = [False, False, False]

    def start(self, score, model_path, draw_image):
        self.model_image = pygame.image.load(model_path)
        self.draw_image = draw_image

        self.score = int(score)
        # Détermine combien d'étoiles sont remplies
        self.filled_stars = 0
        if score >= 70:
            self.filled_stars = 3
        elif score >= 50:
            self.filled_stars = 2
        elif score >= 30:
            self.filled_stars = 1

        self.started = True

    def update(self):
        if self.started:
            # Animation d'entrée de la popup
            if self.popup_y < self.target_y:
                self.popup_y += self.animation_speed

                # Créer des particules pour l'entrée
                if not self.entry_particles_created and self.popup_y > 0:
                    for _ in range(30):
                        self.particles.add_confetti(
                            random.randint(
                                self.popup_x,
                                self.popup_x +
                                self.popup_width),
                            self.popup_y +
                            self.popup_height,
                            count=1)
                    self.entry_particles_created = True

                if self.popup_y >= self.target_y:
                    self.popup_y = self.target_y
                    self.animation_done = True

                    # Plus de particules quand l'animation est terminée
                    for _ in range(40):
                        self.particles.add_confetti(
                            random.randint(
                                self.popup_x,
                                self.popup_x +
                                self.popup_width),
                            self.popup_y,
                            count=1)

            # Animation de remplissage des étoiles
            if self.animation_done and not self.stars_filled:
                all_filled = True
                for i in range(3):
                    if i < self.filled_stars:
                        prev_fill = self.stars_fill[i]
                        self.stars_fill[i] += self.star_animation_speed

                        # Créer des particules quand une étoile est remplie à 100%
                        if prev_fill < 100 and self.stars_fill[i] >= 100:
                            self.stars_fill[i] = 100

                            # Position de l'étoile
                            star_size = 40
                            star_spacing = 120
                            start_x = self.popup_x + \
                                (self.popup_width - star_spacing * 2) // 2 - 20
                            star_y = self.popup_y + 180
                            star_x = start_x + i * star_spacing + star_size // 2

                            # Ajouter des particules d'étoile
                            self.particles.add_particles(
                                star_x, star_y + star_size // 2,
                                GOLD, count=50,
                                speed_range=(1, 4),
                                size_range=(2, 6)
                            )

                        if self.stars_fill[i] < 100:
                            all_filled = False

                        num_stars+=1

                if all_filled:
                    self.stars_filled = True

            # Animation de saut et rotation des étoiles
            if self.stars_filled:
                for i in range(self.filled_stars):
                    # Fonction sinusoïdale pour le saut
                    self.star_jump[i] = -10 * \
                        abs(math.sin(pygame.time.get_ticks() * 0.005 + i * 1.0))
                    # Rotation lente
                    self.star_rotation[i] = 5 * \
                        math.sin(pygame.time.get_ticks() * 0.003 + i * 0.7)

            # Particules en continu
            self.particle_timer += 1
            if self.stars_filled and self.particle_timer % 15 == 0:  # Toutes les 15 frames
                # Ajouter des particules autour du titre
                title_x = self.popup_x + self.popup_width // 2
                title_y = self.popup_y + 30
                self.particles.add_particles(
                    title_x + random.randint(-100, 100),
                    title_y + random.randint(-10, 20),
                    random.choice([GOLD, BLUE, PINK]),
                    count=5
                )

            # Angle de brillance pour les effets
            self.shine_angle = (self.shine_angle + 2) % 360

            # Mettre à jour toutes les particules
            self.particles.update()

    def draw_star(self, x, y, size, fill_percent, jump_offset=0, rotation=0):
        # Créer une surface transparente
        star_surface = pygame.Surface(
            (size * 2, size * 2 + 20), pygame.SRCALPHA)

        points = []
        for i in range(5):
            # Calcul des points extérieurs de l'étoile
            outer_x = x + size * math.cos(math.radians(rotation + i * 72 - 18))
            outer_y = y + jump_offset + size * \
                math.sin(math.radians(rotation + i * 72 - 18)) + 20
            points.append((outer_x - x + size, outer_y - y + size))

            # Calcul des points intérieurs de l'étoile
            inner_x = x + size * 0.4 * \
                math.cos(math.radians(rotation + i * 72 + 18))
            inner_y = y + jump_offset + size * 0.4 * \
                math.sin(math.radians(rotation + i * 72 + 18)) + 20
            points.append((inner_x - x + size, inner_y - y + size))

        # Dessiner le contour de l'étoile
        pygame.draw.polygon(star_surface, BLACK, points, 3)

        # Dessiner le remplissage progressif
        if fill_percent > 0:
            fill_points = points[:int(
                len(points) * min(1, (fill_percent / 100)))]
            if len(fill_points) >= 3:  # Besoin d'au moins 3 points pour un polygone
                pygame.draw.polygon(star_surface, YELLOW, fill_points)

        # Dessiner des effets de brillance pour les étoiles remplies
        if fill_percent >= 100 and self.stars_filled:
            for j in range(4):
                angle = self.shine_angle * math.pi / 180 + j * math.pi / 2
                # Calculer les points de départ et d'arrivée relatifs au centre
                # de la surface
                shine_start_x = size + size * 0.6 * math.cos(angle)
                shine_start_y = size + size * 0.6 * math.sin(angle)
                shine_end_x = size + size * 1.2 * math.cos(angle)
                shine_end_y = size + size * 1.2 * math.sin(angle)

                # Dessiner la ligne brillante
                pygame.draw.line(
                    star_surface,
                    (255, 255, 200, 150),
                    (shine_start_x, shine_start_y),
                    (shine_end_x, shine_end_y),
                    2
                )

        # Ajuster l'opacité si nécessaire
        if fill_percent < 100:
            # Plus opaque à mesure que l'étoile se remplit
            star_surface.set_alpha(max(100, int(fill_percent * 2.55)))

        # Blitter la surface transparente sur l'écran
        self.screen.blit(star_surface, (x - size, y - size - 20))

    def draw(self): 
        if self.started:
            # Dessiner le fond de la popup
            pygame.draw.rect(
                self.screen,
                WHITE,
                (self.popup_x,
                self.popup_y,
                self.popup_width,
                self.popup_height))
            pygame.draw.rect(
                self.screen,
                BLACK,
                (self.popup_x,
                self.popup_y,
                self.popup_width,
                self.popup_height),
                2)

            # Dessiner le titre et le score
            title_surface = MEDIUM_FONT.render("Dessin achevé !!", True, BLACK)
            self.screen.blit(title_surface, (self.popup_x + (self.popup_width -
                        title_surface.get_width()) // 2, self.popup_y + 30))

            score_surface = MEDIUM_FONT.render(f"Score: {self.score}%", True, BLACK)
            self.screen.blit(score_surface, (self.popup_x + (self.popup_width -
                        score_surface.get_width()) // 2, self.popup_y + 80))

            # Dessiner les étoiles
            star_size = 40
            star_spacing = 120
            start_x = self.popup_x + \
                (self.popup_width - star_spacing * 2) // 2 - 20
            star_y = self.popup_y + 180

            # Dessiner les étoiles avec leur animation
            for i in range(3):
                percentage_text = MEDIUM_FONT.render(
                    f"{30 + i * 20}%", True, BLACK)
                self.screen.blit(
                    percentage_text,
                    (start_x +
                    i *
                    star_spacing -
                    percentage_text.get_width() //
                    2 +
                    star_size //
                    2,
                    star_y +
                    star_size +
                    10))

                self.draw_star(
                    start_x + i * star_spacing + star_size // 2,
                    star_y + star_size // 2,
                    star_size,
                    self.stars_fill[i],
                    self.star_jump[i],
                    self.star_rotation[i])

            # Afficher les petites étoiles en haut à droite
            try:
                star_icon = pygame.image.load("assets/icon_star.png")
                star_icon = pygame.transform.scale(star_icon, (40, 40))
                self.screen.blit(
                    star_icon,
                    (self.popup_x +
                    self.popup_width -
                    110,
                    self.popup_y +
                    18))
            except BaseException:
                # Dessiner une étoile simple si l'image n'est pas disponible
                self.draw_star(
                    self.popup_x +
                    self.popup_width -
                    90,
                    self.popup_y +
                    30,
                    20,
                    100)

            self.screen.blit(
                MEDIUM_FONT.render("X"+str(num_stars), True, BLACK),
                (self.popup_x +
                self.popup_width -
                65,
                self.popup_y +
                25))

            # Dessiner les images à droite
            image_x = self.popup_x + self.popup_width + 20
            image_y = self.popup_y + 30

            self.screen.blit(self.model_image, (image_x, image_y))

            # Flèche entre les images
            # Flèche entre les images (inversée mais dans la même zone)
            arrow_points = [
                (image_x + 125, image_y + 190 - 10),  # Point en haut
                (image_x + 145, image_y + 190 - 30),  # Coin bas gauche
                (image_x + 105, image_y + 190 - 30)   # Coin bas droit
            ]
            pygame.draw.polygon(self.screen, GRAY, arrow_points)

            self.screen.blit(self.draw_image, (image_x, image_y + 150 + 50))
            
            # Dessiner toutes les particules
            self.particles.draw( self.screen)
            