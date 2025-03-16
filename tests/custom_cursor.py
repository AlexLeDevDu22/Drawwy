import pygame

# Initialisation
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Charger l'image de la souris une seule fois
custom_cursor = pygame.image.load("tests/model.png").convert_alpha()
custom_cursor = pygame.transform.scale(custom_cursor, (40, 40))

# Cacher la souris Pygame
pygame.mouse.set_visible(False)

def draw_custom_cursor(mouse_pos=None):
    """Dessine le curseur custom à la position actuelle de la souris."""
    if mouse_pos:
        mouse_x, mouse_y = mouse_pos
    else:
        mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.blit(custom_cursor, (mouse_x, mouse_y))

# --- Exemple de boucle principale ---
running = True
while running:
    screen.fill((50, 50, 50))  # Fond gris foncé
    
    # Gérer les événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Appelle la fonction pour dessiner la souris custom sur chaque frame
    draw_custom_cursor()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
