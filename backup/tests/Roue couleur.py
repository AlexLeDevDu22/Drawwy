import pygame

# Initialisation de Pygame
pygame.init()
width, height = 600, 400  # Taille de la fenêtre
ecran = pygame.display.set_mode((width, height))
pygame.display.set_caption("Palette complète")

# Taille de la palette
palette_width, palette_height = 500, 300
palette_x, palette_y = 50, 50  # Position de la palette

# Créer une surface pour stocker la palette
palette_surface = pygame.Surface((palette_width, palette_height))

# Générer les couleurs (dégradé)
for x in range(palette_width):
    for y in range(palette_height):
        hue = (x / palette_width) * 360  # Teinte (0 à 360°)
        saturation = 100  # Saturation maximale
        value = 100 - (y / palette_height) * 100  # Valeur (luminosité)

        color = pygame.Color(0)  # Couleur vide
        color.hsva = (hue, saturation, value, 100)  # Appliquer HSV

        palette_surface.set_at((x, y), color)  # Placer la couleur

# Couleur sélectionnée
selected_color = (255, 255, 255)

running = True
while running:
    ecran.fill((255, 255, 255))  # Fond blanc
    ecran.blit(palette_surface, (palette_x, palette_y))  # Dessiner la palette

    # Affichage de la couleur sélectionnée
    pygame.draw.rect(ecran, selected_color, (width // 2 - 50, 370, 100, 30))
    pygame.draw.rect(ecran, (0, 0, 0), (width // 2 -
                     50, 370, 100, 30), 2)  # Bordure

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Clic pour choisir une couleur
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if palette_x <= mouse_x < palette_x + \
                    palette_width and palette_y <= mouse_y < palette_y + palette_height:
                selected_color = palette_surface.get_at(
                    (mouse_x - palette_x, mouse_y - palette_y))

    pygame.display.flip()

pygame.quit()
