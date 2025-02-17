import pygame

# Initialisation de Pygame
pygame.init()

# Création de la fenêtre
largeur, hauteur = 800, 600
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("Paint")

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

# Définir la résolution de CANVAS (par exemple 50x50 pixels)
canvas_width = 50
canvas_height = 50
CANVAS = [[None for _ in range(canvas_width)] for _ in range(canvas_height)]

# Paramètres pour la zone de dessin sur l'écran
zone_x_min = int(0.2 * largeur)   # 20% de la largeur de la fenêtre
zone_x_max = int(0.8 * largeur)   # 60% de la largeur de la fenêtre
zone_y_min = 0                    # Commence en haut de la fenêtre
zone_y_max = hauteur               # Remplie toute la hauteur de la fenêtre

# Fonction pour dessiner sur le tableau CANVAS
def draw_canvas(canvas, x, y, color, radius):
    height = len(canvas)
    width = len(canvas[0]) if height > 0 else 0

    for i in range(height):
        for j in range(width):
            # Distance au centre (x, y) pour voir si c'est dans le cercle
            if (i - y) ** 2 + (j - x) ** 2 <= radius ** 2:
                canvas[i][j] = color  # Colorier la case

# Fonction pour mettre à jour l'affichage
def update_screen():
    # Calculer les dimensions du pixel à afficher par rapport à CANVAS
    pixel_width = (zone_x_max - zone_x_min) // canvas_width
    pixel_height = (zone_y_max - zone_y_min) // canvas_height

    # Dessiner chaque pixel sur l'écran
    for y in range(canvas_height):
        for x in range(canvas_width):
            color = CANVAS[y][x] if CANVAS[y][x] else BLANC
            pygame.draw.rect(ecran, color, (zone_x_min + x * pixel_width, zone_y_min + y * pixel_height, pixel_width, pixel_height))

# Boucle principale
drawing = False
last_pos = None

running = True
while running:
    ecran.fill(BLANC)  # Fond blanc

    # Affichage du CANVAS à l'écran
    update_screen()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Vérifier si le clic est dans la zone de dessin
            if zone_x_min <= event.pos[0] <= zone_x_max and zone_y_min <= event.pos[1] <= zone_y_max:
                drawing = True
                # Calculer la position du clic dans le tableau CANVAS
                canvas_x = (event.pos[0] - zone_x_min) * canvas_width // (zone_x_max - zone_x_min)
                canvas_y = (event.pos[1] - zone_y_min) * canvas_height // (zone_y_max - zone_y_min)
                draw_canvas(CANVAS, canvas_x, canvas_y, NOIR, 2)  # Dessiner un pixel noir
                last_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
        elif event.type == pygame.MOUSEMOTION and drawing:
            if zone_x_min <= event.pos[0] <= zone_x_max and zone_y_min <= event.pos[1] <= zone_y_max:
                canvas_x = (event.pos[0] - zone_x_min) * canvas_width // (zone_x_max - zone_x_min)
                canvas_y = (event.pos[1] - zone_y_min) * canvas_height // (zone_y_max - zone_y_min)
                draw_canvas(CANVAS, canvas_x, canvas_y, NOIR, 2)  # Dessiner un pixel noir
            last_pos = event.pos

    pygame.display.flip()  # Rafraîchir l'écran

pygame.quit()
