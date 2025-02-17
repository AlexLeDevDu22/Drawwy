import pygame
import sys

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Dessine avec Pygame")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Variables
drawing = False
start_pos = None
shape = "rectangle"  # Forme par défaut
temp_surface = screen.copy()  # Surface temporaire pour le dessin en direct

# Remplir l'écran de blanc
screen.fill(WHITE)

# Boutons
font = pygame.font.SysFont(None, 36)

button_rect = pygame.Rect(10, 10, 120, 40)
button_circle = pygame.Rect(140, 10, 120, 40)
button_line = pygame.Rect(270, 10, 120, 40)

def draw_buttons():
    # Rectangle
    pygame.draw.rect(screen, GRAY, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    text_rect = font.render("Rectangle", True, BLACK)
    screen.blit(text_rect, (button_rect.x + 10, button_rect.y + 10))
    
    # Cercle
    pygame.draw.rect(screen, GRAY, button_circle)
    pygame.draw.rect(screen, BLACK, button_circle, 2)
    text_circle = font.render("Cercle", True, BLACK)
    screen.blit(text_circle, (button_circle.x + 30, button_circle.y + 10))
    
    # Ligne
    pygame.draw.rect(screen, GRAY, button_line)
    pygame.draw.rect(screen, BLACK, button_line, 2)
    text_line = font.render("Ligne", True, BLACK)
    screen.blit(text_line, (button_line.x + 35, button_line.y + 10))

# Boucle principale
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Gestion des clics souris
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                shape = "rectangle"
            elif button_circle.collidepoint(event.pos):
                shape = "circle"
            elif button_line.collidepoint(event.pos):
                shape = "line"
            else:
                drawing = True
                start_pos = event.pos
                temp_surface = screen.copy()  # Sauvegarde l'écran avant de commencer à dessiner

        # Dessin en direct
        if event.type == pygame.MOUSEMOTION:
            if drawing:
                screen.blit(temp_surface, (0, 0))  # Restaure l'écran avant chaque dessin
                end_pos = event.pos
                
                if shape == "rectangle":
                    rect = pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
                    pygame.draw.rect(screen, BLACK, rect, 2)
                elif shape == "circle":
                    radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                    pygame.draw.circle(screen, RED, start_pos, radius, 2)
                elif shape == "line":
                    pygame.draw.line(screen, BLUE, start_pos, end_pos, 2)

        # Fin du dessin
        if event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                drawing = False
                end_pos = event.pos
                
                if shape == "rectangle":
                    rect = pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
                    pygame.draw.rect(screen, BLACK, rect, 2)
                elif shape == "circle":
                    radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                    pygame.draw.circle(screen, RED, start_pos, radius, 2)
                elif shape == "line":
                    pygame.draw.line(screen, BLUE, start_pos, end_pos, 2)

    # Dessiner les boutons
    draw_buttons()

    pygame.display.flip()
