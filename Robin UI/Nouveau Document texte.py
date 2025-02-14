import pygame

# Initialisation de Pygame
pygame.init()

# Dimensions de la fenêtre
largeur, hauteur = 1000, 600
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Interface de dessin")

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

# Définition des zones (x, y, largeur, hauteur)
zones = [
    (200, 50, 600, 500),  # Zone de dessin
    (20, 50, 150, 400),   # Liste personnes
    (20, 470, 150, 80),   # Mot à deviner
    (820, 50, 150, 100),  # Couleurs
    (820, 170, 150, 50),  # Style de stylo
    (820, 240, 150, 200), # Chat
]

# Boucle principale
running = True
while running:
    ecran.fill(BLANC)

    # Dessiner les cadres
    for x, y, w, h in zones:
        pygame.draw.rect(ecran, NOIR, (x, y, w, h), 2)

    pygame.display.flip()

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
