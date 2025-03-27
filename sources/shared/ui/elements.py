from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text

import random
import pygame


class Button:
    def __init__(
            self,
            x,
            y,
            w=None,
            h=None,
            text=None,
            radius=40,
            circle=False,
            text_font=BUTTON_FONT,
            image=None,
            active=True):
        """
        Cr e un bouton avec des param tres de position, de taille, de texte, de police, de rayon, de forme circulaire ou non, d'image, d'activation ou non.

        :param x: La position x du bouton. Si "center", le bouton est centr .
        :type x: int or str
        :param y: La position y du bouton. Si "center", le bouton est centr .
        :type y: int or str
        :param w: La largeur du bouton. Si None, la largeur est calcul e en fonction de la taille de la police.
        :type w: int or None
        :param h: La hauteur du bouton. Si None, la hauteur est calcul e en fonction de la taille de la police.
        :type h: int or None
        :param text: Le texte du bouton. Si None, le bouton n'a pas de texte.
        :type text: str or None
        :param radius: Le rayon du bouton si il est circulaire. Si None, le bouton n'est pas circulaire.
        :type radius: int or None
        :param circle: Le bool enan pour savoir si le bouton est circulaire ou non.
        :type circle: bool
        :param text_font: La police du texte du bouton.
        :type text_font: pygame.font.Font
        :param image: L'image du bouton. Si None, le bouton n'a pas d'image.
        :type image: pygame.Surface or None
        :param active: Le bool enan pour savoir si le bouton est actif ou non.
        :type active: bool
        """
        if not circle:
            self.W = w if w else text_font.size(text)[0] + 40
            self.H = h if h else text_font.size(text)[1] + 36
        else:
            self.W, self.H = radius * 2, radius * 2

        self.X = (pygame.display.Info().current_w -
                  self.W) // 2 if x == "center" else x
        self.Y = (pygame.display.Info().current_h -
                  self.H) // 2 if y == "center" else y
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

    def draw(self, screen, mouse_pos, locked=False):
        """
        Dessine le bouton sur l'cran.

        :param screen: L'cran de jeu.
        :type screen: pygame.display.Surface
        :param mouse_pos: La position de la souris.
        :type mouse_pos: tuple
        :param locked: Si le bouton est verrouill , il n'est pas cliquable.
        :type locked: bool
        """
        self.hover = self.rect.collidepoint(
            mouse_pos) and self.active and not locked

        color = SOFT_ORANGE if self.hover else (
            ORANGE if self.active else self.disabled_color)
        shadow_color = DARK_BEIGE if self.active else (100, 100, 100)
        text_color = BLACK if self.active else (120, 120, 120)

        # Ombre
        pygame.draw.rect(
            screen,
            shadow_color,
            (self.X +
             self.shadow_offset,
             self.Y +
             self.shadow_offset,
             self.W,
             self.H),
            border_radius=self.radius)

        # Bouton principal
        pygame.draw.rect(
            screen,
            color,
            (self.X,
             self.Y,
             self.W,
             self.H),
            border_radius=self.radius)

        if self.text:
            # Texte
            draw_text(self.text,
                      self.text_font,
                      text_color,
                      screen,
                      self.X + self.W // 2,
                      self.Y + self.H // 2 - (2 if self.hover else 0))
        elif self.image:
            # Image
            image = pygame.image.load(self.image)
            image = pygame.transform.smoothscale(
                image, (int(self.W * 0.7), int(self.H * 0.7)))
            # Réduction d'opacité si désactivé
            image.set_alpha(255 if self.active else 180)
            screen.blit(
                image,
                (self.X +
                 self.W *
                 0.15,
                 self.Y +
                 self.H *
                 0.15))

# Classe pour les effets de particules


class Particle:
    def __init__(self, x, y, color):
        """
        Initialize a Particle object with position, color, size, speed, and lifetime.

        :param x: The x-coordinate of the particle.
        :type x: int or float
        :param y: The y-coordinate of the particle.
        :type y: int or float
        :param color: The color of the particle.
        :type color: tuple
        """

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
        pygame.draw.circle(
            surface, self.color, (int(
                self.x), int(
                self.y)), int(
                self.size))


class ColorPicker:
    def __init__(self, x, y, width, height, color_steps=30, dark_steps=12):
        """
        Initialize a ColorPicker object with the given position, size, and color parameters.

        :param x: The x-coordinate of the ColorPicker.
        :type x: int
        :param y: The y-coordinate of the ColorPicker.
        :type y: int
        :param width: The width of the ColorPicker.
        :type width: int
        :param height: The height of the ColorPicker.
        :type height: int
        :param color_steps: The number of color steps to generate. Defaults to 30.
        :type color_steps: int
        :param dark_steps: The number of dark steps to generate. Defaults to 12.
        :type dark_steps: int
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color_steps = color_steps
        self.dark_steps = dark_steps + 1  # Une ligne de plus pour les gris
        self.colors = self.generate_colors()
        self.selected_color = None
        self.selected_pos = None

    def generate_colors(self):
        """
        Generate the colors for the color picker.

        Returns a 2D list of colors, where the first row is a grayscale palette
        and the other rows are color palettes with decreasing brightness.

        :return: A 2D list of colors.
        :rtype: list
        """
        colors = []

        # Première ligne = Nuancier de gris (du blanc au noir)
        gray_row = []
        for i in range(self.color_steps):
            gray_value = int(255 * (1 - i / (self.color_steps - 1)))
            gray_row.append(pygame.Color(gray_value, gray_value, gray_value))
        colors.append(gray_row)

        # Les autres lignes = Teintes colorées
        for j in range(self.dark_steps - 1):
            row = []
            for i in range(self.color_steps):
                hue = i / self.color_steps * 360  # Teinte (HSV)

                saturation = 100
                # Adoucissement de la transition
                brightness = 100 * \
                    ((self.dark_steps - 1 - j) / (self.dark_steps - 1)) ** 0.9

                color = pygame.Color(0)
                color.hsva = (hue, saturation, brightness)
                row.append(color)

            colors.append(row)

        return colors

    def draw(self, surface):
        """
        Draw the color picker onto the given surface.

        This method draws all the colors in the color picker onto the given
        surface. The colors are drawn in a grid with the given size, and the
        currently selected color is highlighted with a white border.

        :param surface: The surface to draw onto.
        :type surface: pygame.Surface
        """
        step_w = self.rect.width // self.color_steps
        step_h = self.rect.height // self.dark_steps

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
            pygame.draw.rect(surface, (255, 255, 255),
                             (px, py, step_w, step_h), 2)

    def get_color_at(self, pos):
        """
        Get the color at the given position.

        If the given position is within the color picker's rectangle,
        this method returns the color at that position as a tuple of
        three integers (red, green, blue). If the position is not
        within the color picker, this method returns None.

        :param pos: The position to get the color at.
        :type pos: tuple
        :return: The color at the given position, or None if the position is not within the color picker.
        :rtype: tuple or None
        """
        x, y = pos
        if self.rect.collidepoint(x, y):
            step_w = self.rect.width // self.color_steps
            step_h = self.rect.height // self.dark_steps
            i = (x - self.rect.x) // step_w
            j = (y - self.rect.y) // step_h
            try:
                self.selected_color = self.colors[j][i]
            except IndexError:
                return None
            self.selected_pos = (
                self.rect.x + i * step_w,
                self.rect.y + j * step_h)
            return (
                self.selected_color.r,
                self.selected_color.g,
                self.selected_color.b)
        return None
