from shared.ui.common_ui import *
from shared.ui.elements import *
from SoloGame.ui.elements import FloatingObject
from shared.utils.data_manager import *

import pygame
import sys
import math
import random
from pygame import gfxdraw
try:
    from pygame_emojis import load_emoji
except BaseException:
    import pygame.freetype


class ThemeCard:
    def __init__(self, x, y, width, height, theme_info):
        """
        Initialize a ThemeCard object with specified position, dimensions, and theme information.

        :param x: The x-coordinate of the card's position.
        :type x: int
        :param y: The y-coordinate of the card's position.
        :type y: int
        :param width: The width of the card.
        :type width: int
        :param height: The height of the card.
        :type height: int
        :param theme_info: A dictionary containing theme-specific information such as color.
        :type theme_info: dict
        """

        self.rect = pygame.Rect(x, y, width, height)
        self.y = y
        self.theme_info = theme_info
        self.color = theme_info["color"]
        self.light_color = self.lighten_color(self.color, 30)
        self.is_hovered = False
        self.is_selected = False
        self.animation_progress = 0
        self.hover_scale = 1.0
        self.rotation = 0
        self.particles = []

    def lighten_color(self, color, amount):
        return tuple(min(255, c + amount) for c in color)

    def draw(self, screen):
        """
        Draws the theme card on the screen with animations and effects.

        This method handles the hover and selection animations for the theme card,
        updating the animation progress accordingly. It also manages the creation and
        movement of particles when the card is selected, and ensures expired particles
        are removed.

        The card is drawn with a hover scaling effect, and if selected, additional
        effects such as a border and glow are rendered. The theme icon is displayed
        using emojis if available, otherwise a fallback font is used. The theme name
        is drawn at the bottom of the card.

        :param screen: The surface on which to draw the theme card.
        :type screen: pygame.Surface
        """

        # Animation de survol
        if (self.is_hovered or self.is_selected) and self.animation_progress < 1:
            self.animation_progress += 0.1
        elif not self.is_hovered and not self.is_selected and self.animation_progress > 0:
            self.animation_progress -= 0.1

        self.animation_progress = max(0, min(1, self.animation_progress))

        # Animation de sélection
        if self.is_selected:
            self.rotation = (self.rotation + 1) % 360

            # Ajouter des particules quand sélectionné
            if random.random() < 0.2:
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                size = random.uniform(3, 6)
                life = random.uniform(20, 40)
                px = self.rect.centerx + \
                    random.uniform(-self.rect.width / 2, self.rect.width / 2)
                py = self.rect.centery + \
                    random.uniform(-self.rect.height / 2, self.rect.height / 2)
                self.particles.append({
                    'x': px, 'y': py,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': size, 'life': life,
                    'color': self.light_color
                })

        # Mettre à jour et dessiner les particules
        for i, particle in enumerate(self.particles):
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            alpha = int(255 * (abs(particle['life']) / 40))
            particle_color = (*particle['color'], alpha)

            gfxdraw.filled_circle(screen,
                                  int(particle['x']),
                                  int(particle['y']),
                                  int(particle['size']),
                                  particle_color)

        # Supprimer les particules expirées
        self.particles = [p for p in self.particles if p['life'] > 0]

        # Échelle pour effet de survol
        self.hover_scale = 1.0 + 0.08 * self.animation_progress
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)

        # Position centrée pour l'animation
        scaled_x = self.rect.x + (self.rect.width - scaled_width) // 2
        scaled_y = self.rect.y + (self.rect.height - scaled_height) // 2

        # Couleur interpolée
        color = [
            int(self.color[i] + (self.light_color[i] - self.color[i]) * self.animation_progress)
            for i in range(3)
        ]

        # Dessiner la bordure si sélectionnée
        if self.is_selected:
            border_rect = pygame.Rect(
                scaled_x - 10,
                scaled_y - 10,
                scaled_width + 20,
                scaled_height + 20)
            pygame.draw.rect(screen, WHITE, border_rect, border_radius=20)

            # Effet de brillance autour de la carte
            for i in range(5):
                glow_size = 5 - i
                glow_rect = pygame.Rect(
                    border_rect.x - glow_size,
                    border_rect.y - glow_size,
                    border_rect.width + glow_size * 2,
                    border_rect.height + glow_size * 2
                )
                glow_color = (*self.light_color, 50 - i * 10)
                pygame.draw.rect(
                    screen,
                    glow_color,
                    glow_rect,
                    border_radius=25,
                    width=2)

        # Dessiner la carte
        scaled_rect = pygame.Rect(
            scaled_x, scaled_y, scaled_width, scaled_height)
        pygame.draw.rect(screen, color, scaled_rect, border_radius=15)

        # Dessiner l'icône
        icone_texte = MEDIUM_FONT.render(self.theme_info["icon"], True, WHITE)
        icone_rect = icone_texte.get_rect(
            center=(
                scaled_rect.centerx,
                scaled_rect.centery - 30))
        screen.blit(icone_texte, icone_rect)

        try:  # pygame emojis
            screen.blit(
                load_emoji(
                    self.theme_info["icon"],
                    (16 / 100 * H,
                     16 / 100 * H)),
                (scaled_rect.centerx - 85,
                 scaled_rect.centery - 108))
        except BaseException:  # pygame freetype
            seguisy80 = pygame.freetype.SysFont("segoeuisymbol", 135)
            emoji, rect = seguisy80.render(self.theme_info["icon"], "black")
            rect.center = (scaled_rect.centerx, scaled_rect.centery)
            screen.blit(emoji, rect)

        # Dessiner le name du thème
        name_texte = MEDIUM_FONT.render(
            self.theme_info["name"], True, SOFT_ORANGE)
        name_rect = name_texte.get_rect(
            center=(
                scaled_rect.centerx + 2,
                scaled_rect.centery + 65))
        screen.blit(name_texte, name_rect)

        name_texte = MEDIUM_FONT.render(self.theme_info["name"], True, WHITE)
        name_rect = name_texte.get_rect(
            center=(
                scaled_rect.centerx,
                scaled_rect.centery + 63))
        screen.blit(name_texte, name_rect)


def draw_background(screen):
    # Dégradé de fond
    for y in range(H):
        # Interpolation entre deux couleurs pour créer un dégradé
        color = [
            int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / H))
            for i in range(3)
        ]
        pygame.draw.line(screen, color, (0, y), (W, y))


def theme_choicer(screen, cursor):
    """
    Displays the theme selection screen for Solo mode.

    This screen allows the user to choose a theme for the game by
    interacting with theme cards. The user can hover over cards to
    highlight them and click to select. Once a theme is selected, the
    user can proceed to the image selection or exit the game.

    :param screen: The surface on which to draw the theme selection screen.
    :type screen: pygame.Surface
    :param cursor: The custom cursor object to display.
    :type cursor: CustomCursor
    :return: A tuple containing the screen, the next page ("images" or "exit"),
             and the selected theme.
    :rtype: tuple
    """

    global W, H
    W, H = pygame.display.Info().current_w, pygame.display.Info().current_h
    # Créer les cartes de thèmes
    theme_width, theme_height = 200, 200
    theme_cards = []

    for i, theme in enumerate(SOLO_THEMES):
        x = W // 2 - (len(SOLO_THEMES) * (theme_width + 30)
                      ) // 2 + i * (theme_width + 30)
        y = H // 3
        theme_cards.append(ThemeCard(x, y, theme_width, theme_height, theme))
    # Créer le bouton de démarrage
    start_button = Button(
        "center",
        H // 3 * 2 - 20,
        text="Commencer",
        active=False)
    quit_button = Button("center", H // 3 * 2 + 110, text="Quitter")

    # Créer des objets flottants pour l'arrière-plan
    floating_objects = []
    for _ in range(30):
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

    # Variables de jeu
    selected_theme = None
    running = True

    clock = pygame.time.Clock()

    # Animation d'introduction
    intro_alpha = 255
    intro_stage = 0
    intro_timer = 0

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for i, card in enumerate(theme_cards):
            if card.rect.collidepoint(mouse_pos):
                card.is_hovered = True
            else:
                card.is_hovered = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and intro_stage >= 2:
                # Vérifier les clics sur les cartes de thèmes
                for i, card in enumerate(theme_cards):
                    if card.is_hovered:
                        # Désélectionner toutes les cartes
                        for c in theme_cards:
                            c.is_selected = False
                        # Sélectionner la carte cliquée
                        card.is_selected = True
                        selected_theme = SOLO_THEMES[i]

                        start_button.active = True

                # Vérifier le clic sur le bouton de démarrage
                if start_button.rect.collidepoint(
                        mouse_pos) and selected_theme is not None:
                    return screen, "images", selected_theme
                if quit_button.rect.collidepoint(mouse_pos):
                    return screen, "exit", selected_theme

        # Mettre à jour les survols
        if intro_stage >= 2:
            for card in theme_cards:
                card.rect.collidepoint(mouse_pos)

        # Mettre à jour les objets flottants
        for obj in floating_objects:
            obj.update()

        # Dessiner l'arrière-plan
        draw_background(screen)

        # Dessiner les objets flottants
        for obj in floating_objects:
            obj.draw(screen)

        # Animation d'introduction
        if intro_stage == 0:
            # Fondu d'entrée
            intro_alpha -= 3
            if intro_alpha <= 0:
                intro_alpha = 0
                intro_stage = 1
                intro_timer = 60  # Attendre 1 seconde

            # Dessiner un rectangle noir qui disparaît
            intro_surf = pygame.Surface((W, H))
            intro_surf.fill(BLACK)
            intro_surf.set_alpha(intro_alpha)
            screen.blit(intro_surf, (0, 0))

        elif intro_stage == 1:
            # Attendre un moment
            intro_timer -= 1
            if intro_timer <= 0:
                intro_stage = 2

        else:

            # Dessiner le sous-titre
            subtitle = BUTTON_FONT.render("Selectionne un theme", True, WHITE)
            subtitle_rect = subtitle.get_rect(center=(W // 2, 200))
            screen.blit(subtitle, subtitle_rect)

            # Dessiner les cartes de thèmes
            for i, card in enumerate(theme_cards):
                card.rect.y = card.y + \
                    math.sin((pygame.time.get_ticks() + 16000 / len(theme_cards) * i) / 1000) * 16
                card.draw(screen)

            # Dessiner le bouton de démarrage
            start_button.draw(screen, mouse_pos)
            quit_button.draw(screen, mouse_pos)

        # Mettre à jour l'affichage
        cursor.show(screen, mouse_pos, True in pygame.mouse.get_pressed())
        pygame.display.flip()
        clock.tick(CONFIG["fps"])
