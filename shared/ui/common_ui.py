import pygame
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (140, 140, 140)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (65, 105, 225)
LIGHT_BLUE = (119, 181, 254)
VERY_LIGHT_BLUE= (160, 205, 255)
ORANGE = (255, 95, 31)
SOFT_ORANGE = (255, 160, 122)
HIDED_ORANGE = (255, 110, 55, 220)
BEIGE = (245, 222, 179)
DARK_BEIGE = (222, 184, 135)
PASTEL_PINK = (255, 209, 220)
PASTEL_GREEN = (193, 225, 193)
PASTEL_YELLOW = (253, 253, 150)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
LIGHT_BEIGE = (239, 231, 219)
LIGHT_ORANGE = (255, 219, 187)
PINK = (255, 130, 186)
YELLOW = (255, 223, 97)
PURPLE = (130, 94, 196)
LIGHT_PURPLE = (157, 127, 211)
GOLD = (255, 215, 0)
# Police personnalisée
pygame.init()
TITLE_FONT = pygame.font.Font(None, 300)
BUTTON_FONT = pygame.font.Font(None, 70)
MEDIUM_FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font( pygame.font.match_font("segoeuisymbol" if sys.platform.startswith("win") else "dejavusans"), 26)
VERY_SMALL_FONT = pygame.font.Font(None, 25)


class CustomCursor:
    def __init__(self, cursor_path):
        self.custom_cursor = bool(cursor_path)
        pygame.mouse.set_visible(not self.custom_cursor)

        if self.custom_cursor:
            self.cursor_default = pygame.transform.scale(
                pygame.image.load(cursor_path).convert_alpha(), (35, 35)
            )
            self.cursor = self.cursor_default

            # Si "anime" est dans le nom du fichier, charger un curseur alternatif
            if "anime" in cursor_path:
                self.cursor_click = pygame.transform.scale(
                    pygame.image.load(cursor_path.replace("anime", "click")).convert_alpha(), (35, 35)
                )
            else:
                self.cursor_click = self.cursor_default  # Pas d'animation, reste le même

    def handle_event(self, event):
        """Change le curseur si 'anime' est dans le nom du fichier"""
        if self.custom_cursor and "anime" in pygame.image.get_extended():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.cursor = self.cursor_click
            elif event.type == pygame.MOUSEBUTTONUP:
                self.cursor = self.cursor_default

    def show(self, screen, mouse_pos=None):
        if self.custom_cursor:
            if mouse_pos:
                mouse_x, mouse_y = mouse_pos
            else:
                mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(self.cursor, (mouse_x, mouse_y))