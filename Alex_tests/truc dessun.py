import pygame
import sys

# Initialiser Pygame
pygame.init()

# Définir les dimensions de la fenêtre
width, height = 800, 600
margin = 50  # Marge autour de la zone de dessin
draw_area = pygame.Rect(margin, margin, width - 2 * margin, height - 2 * margin)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dessiner avec la souris")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Variables pour le dessin
drawing = False
last_pos = None
current_color = BLUE  # Couleur initiale

# Ouvrir un fichier pour enregistrer les pixels dessinés
file = open("pixels.txt", "w")

# Fonction pour dessiner une ligne et enregistrer les pixels modifiés
def draw_line(screen, start, end, color, width=3):
    if draw_area.collidepoint(start) and draw_area.collidepoint(end):
        pygame.draw.line(screen, color, start, end, width)
        save_pixel_data(start, color)
        save_pixel_data(end, color)

# Fonction pour enregistrer les pixels dans le fichier
def save_pixel_data(pos, color):
    x, y = pos
    r, g, b = color  # Corrigé : seulement R, G, B
    file.write(f"{x}, {y}, {r}, {g}, {b}\n")

# Remplir l'écran en blanc
screen.fill(WHITE)

# Dessiner la bordure autour de la zone de dessin
pygame.draw.rect(screen, BLACK, draw_area, 5)

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if draw_area.collidepoint(event.pos):  # Vérifie si le clic est dans la zone
                drawing = True
                last_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
        elif event.type == pygame.MOUSEMOTION and drawing:
            current_pos = pygame.mouse.get_pos()
            draw_line(screen, last_pos, current_pos, current_color)
            last_pos = current_pos
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                current_color = RED
            elif event.key == pygame.K_g:
                current_color = GREEN
            elif event.key == pygame.K_b:
                current_color = BLUE

    # Redessiner la bordure après chaque mise à jour
    pygame.draw.rect(screen, BLACK, draw_area, 5)

    # Mettre à jour l'affichage
    pygame.display.flip()

# Fermer le fichier à la fin du programme
file.close()

# Quitter Pygame
pygame.quit()
sys.exit()
