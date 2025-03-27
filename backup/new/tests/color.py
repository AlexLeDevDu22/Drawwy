import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 900, 600
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Configuration de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Color Picker")
clock = pygame.time.Clock()


class ColorPicker:
    def __init__(self, x, y, width, height, color_steps=30, dark_steps=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_steps = color_steps  # Beaucoup plus de teintes
        self.dark_steps = dark_steps  # Plus de niveaux d'assombrissement
        self.colors = self.generate_colors()
        self.selected_color = None
        self.selected_pos = None
        self.is_holding = False  # État du clic maintenu

    def generate_colors(self):
        colors = []
        for j in range(self.dark_steps):
            row = []
            for i in range(self.color_steps):
                hue = i / self.color_steps * 360  # Teinte (HSV)
                # Assombrissement progressif
                brightness = 1 - (j / (self.dark_steps - 1))
                color = pygame.Color(0)
                color.hsva = (hue, 100, brightness * 100)
                row.append(color)
            colors.append(row)
        return colors

    def draw(self, surface):
        step_w = self.rect.width // self.color_steps
        step_h = self.rect.height // self.dark_steps

        # Dessiner la grille de couleurs
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
            pygame.draw.rect(surface, WHITE, (px, py, step_w, step_h), 3)

    def get_color_at(self, pos):
        x, y = pos
        if self.rect.collidepoint(x, y):
            step_w = self.rect.width // self.color_steps
            step_h = self.rect.height // self.dark_steps
            i = (x - self.rect.x) // step_w
            j = (y - self.rect.y) // step_h
            self.selected_color = self.colors[j][i]
            self.selected_pos = (
                self.rect.x + i * step_w,
                self.rect.y + j * step_h)
            return self.selected_color
        return None


# Création du Color Picker
picker = ColorPicker(100, 100, 600, 300, color_steps=30, dark_steps=15)

# Boucle principale
running = True
while running:
    screen.fill((30, 30, 30))  # Fond gris foncé

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            picker.is_holding = True
            picker.get_color_at(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            picker.is_holding = False

    # Si le clic est maintenu, on met à jour la sélection
    if picker.is_holding:
        picker.get_color_at(pygame.mouse.get_pos())

    # Dessiner le picker
    picker.draw(screen)

    # Afficher la couleur sélectionnée
    if picker.selected_color:
        pygame.draw.rect(screen, picker.selected_color, (750, 200, 120, 120))
        pygame.draw.rect(screen, BLACK, (750, 200, 120, 120), 3)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
