from sympy import im
from shared.ui.common_ui import *
from shared.ui.elements import Button
from SoloGame.ui.elements import FloatingObject
from shared.utils.data_manager import *

import pygame
import sys
import math
import random
from pygame import gfxdraw
import time


class ImageCarousel:
    def __init__(self, X, Y, images, theme):
        """
        Initialisation de l'objet ImageCarousel.

        :param X: La position centrale en X du carousel.
        :param Y: La position centrale en Y du carousel.
        :param images: La liste des images à afficher dans le carousel.
        :param theme: Le thème associé au carousel, permettant de récupérer les couleurs et les polices.
        """
        self.W = W
        self.H = H
        self.carousel_height = 200
        self.size = 0.6 * H
        self.rect = pygame.Rect(
            (X - self.size) // 2,
            (Y - self.size) // 2,
            self.size,
            self.size)
        self.images = images
        self.theme = theme
        self.current_offset = 0  # Position actuelle des images
        self.deceleration = 0.2  # Décélération progressive
        self.is_spinning = False
        self.selection_time = 0
        self.selection_delay = 3  # Temps avant l'arrêt
        self.shake_intensity = 0
        self.selected_image = None
        self.spin_speed = 0
        self.max_spin_speed = 40
        self.particles = []
        self.images_opacity = 0

        star_icon = pygame.image.load("assets/icon_star.png").convert_alpha()
        self.star_icon = pygame.transform.scale(star_icon, (30, 30))

    def start_spin(self):
        """
        Initiates the spinning of the image carousel with a random speed.

        This method sets the carousel to a spinning state by assigning a random
        initial spin speed between a defined range and calculates the time at which
        the selection process will complete. The spinning continues until the
        selection delay time has passed.
        """
        self.is_spinning = True
        self.spin_speed = random.randint(
            self.max_spin_speed - 20,
            self.max_spin_speed)  # Relancer avec la vitesse max
        self.selection_time = time.time() + self.selection_delay

    def update(self):
        """
        Updates the image carousel's position and spinning state.

        This method is called once per frame and updates the position of the
        carousel based on its spinning state. If the carousel is spinning,
        it will continue to spin until the selection delay time has passed.
        Once the selection delay has passed, the carousel will slow down and
        eventually stop at a random position. The selected image is then
        stored in the `selected_image` attribute.

        The method also updates the opacity of the images and adds particles
        to celebrate the selection of an image.
        """
        if self.is_spinning:
            self.current_offset += self.spin_speed
            self.current_offset %= len(
                self.images) * self.carousel_height  # Boucle continue
            current_time = time.time()
            self.images_opacity = min(1, self.images_opacity + 0.01)

            if current_time >= self.selection_time:
                distance_to_target = (
                    self.carousel_height // 2 - self.current_offset % self.carousel_height) % self.carousel_height
                if self.spin_speed > 0:
                    self.spin_speed = max(
                        0,
                        self.spin_speed -
                        random.uniform(
                            self.deceleration,
                            self.deceleration *
                            2))
                    if distance_to_target < 10 and self.spin_speed < 5:
                        self.spin_speed = max(0.5, self.spin_speed - 0.5)
                else:
                    if distance_to_target > 1:
                        if distance_to_target <= self.carousel_height // 2:
                            self.current_offset += math.sqrt(
                                distance_to_target)
                        else:
                            self.current_offset -= math.sqrt(
                                distance_to_target)
                    else:
                        self.is_spinning = False
                        self.selected_image = (
                            round(self.current_offset / self.carousel_height) + 1) % len(self.images)

                        self.shake_intensity = 0

                        # Ajouter des particules pour célébrer la sélection
                        for _ in range(50):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(2, 6)
                            size = random.uniform(3, 8)
                            life = random.uniform(70, 100)
                            color = random.choice([YELLOW, PINK, GREEN, BLUE])
                            self.particles.append({
                                'x': self.rect.centerx,
                                'y': self.rect.centery,
                                'vx': math.cos(angle) * speed,
                                'vy': math.sin(angle) * speed,
                                'size': size,
                                'life': life,
                                'color': color
                            })

            self.shake_intensity = max(
                0,
                self.shake_intensity -
                0.1) if not self.is_spinning else min(
                10,
                self.shake_intensity +
                0.2)

        # Mettre à jour les particules
        for i, particle in enumerate(self.particles):
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravité
            particle['life'] -= 1

        # Supprimer les particules expirées
        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self, surface):
        """
        Draws the image carousel and associated effects onto the given surface.

        This method iterates over the images in the carousel, applying visual effects
        such as shaking and scaling based on the current spinning state. It also draws
        stars and particles to create a dynamic visual presentation. The images are
        rendered with rounded corners and varying opacities, and the entire carousel
        may exhibit a shaking effect to simulate dynamic movement.

        :param surface: The Pygame surface on which to render the carousel and effects.
        :type surface: pygame.Surface
        """

        center_x = self.rect.centerx
        for i, img in enumerate(self.images):
            shake_x = random.uniform(-self.shake_intensity * (self.spin_speed / self.max_spin_speed),
                                     self.shake_intensity * (self.spin_speed / self.max_spin_speed))
            shake_y = random.uniform(-self.shake_intensity * (self.spin_speed / self.max_spin_speed),
                                     self.shake_intensity * (self.spin_speed / self.max_spin_speed))

            pos_x = (i * self.carousel_height - self.current_offset + center_x) % (
                len(self.images) * self.carousel_height) - self.carousel_height // 2
            scale_factor = max(0.2, 1 - abs(center_x - pos_x) / (self.W // 2))
            alpha = max(0, 255 * scale_factor * self.images_opacity)

            scaled_img = pygame.transform.scale(img, (int(
                self.carousel_height * scale_factor), int(self.carousel_height * scale_factor)))
            img_surface = pygame.Surface(
                scaled_img.get_size(), pygame.SRCALPHA)

            # Créer un rectangle avec des coins arrondis pour le masque
            mask = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(
                mask, (255, 255, 255), mask.get_rect(), border_radius=20)

            # Appliquer le masque arrondi à l'image
            img_surface.fill((255, 255, 255, int(alpha)))
            img_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            img_surface.blit(
                scaled_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # image stars
            size = self.star_icon.get_height() * max(0.3, scale_factor)
            for j in range(self.theme["images"][i]["stars"]):
                star_icon = pygame.transform.scale(
                    self.star_icon, (size, size))
                img_surface.blit(star_icon,
                                 (10 + j * int(size * 1.25),
                                  scaled_img.get_height() - 8 - size))

            # Blitter l'image arrondie sur la surface principale
            surface.blit(
                img_surface,
                (pos_x -
                 scaled_img.get_width() //
                 2,
                 self.rect.centery -
                 scaled_img.get_height() //
                 2))

        transparent_surface = pygame.Surface(
            (self.carousel_height,
             self.carousel_height),
            pygame.SRCALPHA)  # Taille du rectangle
        transparent_surface.fill((0, 0, 0, 0))  # Totalement transparent

        main_frame_rect = pygame.Rect(
            self.rect.centerx - self.carousel_height // 2,
            self.rect.centery - self.carousel_height // 2,
            self.carousel_height,
            self.carousel_height
        )
        # Appliquer les tremblements
        shake_x = random.uniform(-self.shake_intensity * (self.spin_speed / self.max_spin_speed),
                                 self.shake_intensity * (self.spin_speed / self.max_spin_speed))
        shake_y = random.uniform(-self.shake_intensity * (self.spin_speed / self.max_spin_speed),
                                 self.shake_intensity * (self.spin_speed / self.max_spin_speed))
        main_frame_rect.x += shake_x
        main_frame_rect.y += shake_y

        # Dessiner le rectangle avec des bordures uniquement (intérieur
        # transparent)
        border_color = (255, 255, 255)  # Blanc
        border_radius = 20  # Coins arrondis
        border_width = 5  # Épaisseur des bordures

        pygame.draw.rect(
            surface,
            border_color,
            main_frame_rect,
            width=border_width,
            border_radius=border_radius)

        # Dessiner les particules
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 100))
            particle_color = (*particle['color'], alpha)
            gfxdraw.filled_circle(
                surface,
                int(particle['x']),
                int(particle['y']),
                int(particle['size']),
                particle_color
            )


def draw_background(surface):
    # Dégradé de fond bleu clair
    for y in range(H):
        # Interpolation entre deux colors pour créer un dégradé
        color = [
            int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / H))
            for i in range(3)
        ]
        pygame.draw.line(surface, color, (0, y), (W, y))


def image_selector(screen, cursor, theme):
    """
    Page de sélection d'image pour le mode Solo.

    Cette page permet de sélectionner une image parmi celles proposées par le thème
    actuel. L'utilisateur peut lancer une roulette pour sélectionner une image
    aléatoirement. Une fois une image sélectionnée, l'utilisateur peut lancer le
    compte à rebours pour démarrer la page de dessin.

    :param screen: La surface de l'écran.
    :param cursor: L'objet curseur.
    :param theme: Le thème actuel.
    :return: La prochaine page à afficher (soit "themes" pour revenir au menu
             des thèmes, soit "play" pour lancer la page de dessin) et l'image
             sélectionnée.
    """
    global W, H
    W, H = pygame.display.Info().current_w, pygame.display.Info().current_h

    # Générer des images d'exemple pour le thème sélectionné
    images = [pygame.image.load(
        f"assets/soloImages/{theme["path"]}{image["path"]}") for image in theme["images"]]

    # Créer la roulette d'images
    image_roulette = ImageCarousel(W, H, images, theme)

    # Créer le bouton pour lancer la roulette
    spin_button = Button(
        (W - (BUTTON_FONT.size("Tourner")[0] + 90)) // 2, H * 0.7, text="Tourner")

    # Créer le bouton pour commencer à dessiner (initialement désactivé)
    start_drawing_button = Button((W -
                                   (BUTTON_FONT.size("Tourner")[0] +
                                    70)) //
                                  2 +
                                  BUTTON_FONT.size("Tourner")[0] +
                                  40, H *
                                  0.7, w=100, h=100, image="assets/valid.svg")

    back_button = Button("center", H * 0.7 + 130, text="Retour")

    # Créer des objets flottants pour l'arrière-plan
    floating_objects = []
    for _ in range(15):
        x = random.randint(-100, W + 100)
        y = random.randint(0, H)
        size = random.randint(5, 15)
        color_choice = random.choice([PINK, YELLOW, BLUE, GREEN])
        speed = random.uniform(0.2, 0.8)
        floating_objects.append(
            FloatingObject(
                x,
                y,
                size,
                color_choice,
                speed,
                W))

    # Variables d'état
    countdown_start_time = 0
    show_countdown = False

    clock = pygame.time.Clock()

    image_roulette.start_spin()
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier le clic sur le bouton de rotation
                if spin_button.hover and not image_roulette.is_spinning:
                    image_roulette.start_spin()

                # Vérifier le clic sur le bouton de dessin
                if start_drawing_button.hover and image_roulette.selected_image is not None and not image_roulette.is_spinning:
                    # Lancer le compte à rebours
                    if not show_countdown:
                        show_countdown = True
                        countdown_start_time = time.time()

                if back_button.hover:
                    return screen, "themes", image_roulette.selected_image

        # Mettre à jour les survols

        start_drawing_button.active = image_roulette.selected_image is not None and not image_roulette.is_spinning

        # Mettre à jour les objets flottants
        for obj in floating_objects:
            obj.update()

        # Mettre à jour la roulette d'images
        image_roulette.update()

        # Dessiner l'arrière-plan
        draw_background(screen)

        # Dessiner les objets flottants
        for obj in floating_objects:
            obj.draw(screen)

        # Dessiner le sous-titre avec le thème sélectionné
        subtitle = BUTTON_FONT.render(f"Theme: {theme["name"]}", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(W // 2, 220))
        screen.blit(subtitle, subtitle_rect)

        # Dessiner la roulette d'images
        image_roulette.draw(screen)

        # Dessiner le bouton de rotation
        if not image_roulette.selected_image or not image_roulette.is_spinning:
            spin_button.draw(screen, mouse_pos)

        # Dessiner le bouton de dessin si une image est sélectionnée
        if image_roulette.selected_image is not None:
            start_drawing_button.draw(screen, mouse_pos)

        back_button.draw(screen, mouse_pos)

        # Afficher le compte à rebours si actif
        if show_countdown:
            elapsed = time.time() - countdown_start_time
            if elapsed < 3:
                countdown_value = 3 - int(elapsed)
                countdown_text = BUTTON_FONT.render(
                    str(countdown_value), True, WHITE)
                countdown_rect = countdown_text.get_rect(
                    center=(W // 2, H // 2))

                # Ajouter un effet de pulsation
                scale = 1.0 + 0.2 * math.sin(elapsed * 10)
                countdown_text = pygame.transform.scale(countdown_text, (int(
                    countdown_rect.w * scale), int(countdown_rect.h * scale)))
                countdown_rect = countdown_text.get_rect(
                    center=(W // 2, H // 2))

                # Dessiner un cercle d'arrière-plan
                pygame.draw.circle(
                    screen, PURPLE, (W // 2, H // 2), 80 * scale, 0)
                screen.blit(countdown_text, countdown_rect)
            else:
                # Le compte à rebours est terminé, on lancerait normalement la
                # prochaine page
                show_countdown = False

                return screen, "play", image_roulette.selected_image

        # Mettre à jour l'affichage
        cursor.show(screen, mouse_pos, True in pygame.mouse.get_pressed())
        pygame.display.flip()
        clock.tick(CONFIG["fps"])
