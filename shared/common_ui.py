import pygame
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (170, 170, 170)
LIGHT_GRAY = (200, 200, 200)
LIGHT_BLUE = (119, 181, 254)
DARK_BLUE = (65, 105, 225)
ORANGE = (255, 95, 31)
SOFT_ORANGE = (255, 160, 122)
BEIGE = (245, 222, 179)
DARK_BEIGE = (222, 184, 135)
PASTEL_PINK = (255, 209, 220)
PASTEL_GREEN = (193, 225, 193)
PASTEL_YELLOW = (253, 253, 150)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (0,0,255)


# Police personnalisée
pygame.init()
TITLE_FONT = pygame.font.Font(None, 300)
BUTTON_FONT = pygame.font.Font(None, 80)
MEDIUM_FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font( pygame.font.match_font("segoeuisymbol" if sys.platform.startswith("win") else "dejavusans"), 26)
VERY_SMALL_FONT = pygame.font.Font(None, 25)
pygame.quit()