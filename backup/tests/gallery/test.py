import pygame
import sys
import json
import cv2
import numpy as np

### --- CHARGEMENT DES DONNÉES --- ###

with open("tests/gallery/gallery_data.json", "r") as f:
    rooms = json.load(f)

pygame.init()
screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h))
W, H = screen.get_size()
clock = pygame.time.Clock()


wall = pygame.image.load("tests/gallery/assets/wall3.jpg").convert()
line = pygame.image.load("tests/gallery/assets/line.png").convert_alpha()
parquet = pygame.image.load("tests/gallery/assets/parquet.jpg").convert()

WALL_SIZE = int(0.8 * H)
LINE_SIZE = W
PERSPECTIVE=0.6

wall = pygame.transform.scale(wall, (WALL_SIZE, WALL_SIZE))
line = pygame.transform.scale(line, (LINE_SIZE, LINE_SIZE * 0.01))
parquet = pygame.transform.scale(parquet, (WALL_SIZE, (H-WALL_SIZE)*(1/PERSPECTIVE)))

# Largeur totale du sol pour permettre le déplacement
CORRIDOR_WIDTH = int(W+PERSPECTIVE*2*W)
FLOOR_HEIGHT = int(0.9 * WALL_SIZE)

# --- TRANSFORMATION EN PERSPECTIVE --- #
cached_parquet=None
def perspective_parquet(parquet, view_pos):
    """Transforme et affiche le sol avec une meilleure gestion de la perspective."""
    global cached_parquet

    # Création de la surface sol
    surface = pygame.Surface((CORRIDOR_WIDTH, FLOOR_HEIGHT)).convert()

    # Remplissage du sol avec le parquet
    for x in range(0, CORRIDOR_WIDTH, parquet.get_width()):
        surface.blit(parquet, (x, 0))

    # Ajustement de l'offset pour correspondre au déplacement horizontal
    offset = -view_pos % parquet.get_width()
    new_surface = pygame.Surface((surface.get_width(), FLOOR_HEIGHT))
    new_surface.blit(surface, (offset, 0),(0,0,surface.get_width()-offset, FLOOR_HEIGHT))

    # Transformation en perspective (une seule fois si possible)
    if cached_parquet is None:
        arr = pygame.surfarray.array3d(new_surface)
        arr = np.transpose(arr, (1, 0, 2))
        h, w = arr.shape[:2]

        # Points sources et cibles pour la transformation perspective
        top_w = w * PERSPECTIVE
        dx = (w - top_w) / 2
        src_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        dst_pts = np.float32([[dx, 0], [dx + top_w, 0], [0, h], [w, h]])

        # Matrice de transformation perspective
        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)

        # Application de la transformation
        transformed = cv2.warpPerspective(arr, matrix, (w, h))
        transformed = np.transpose(transformed, (1, 0, 2))

        cached_parquet = pygame.surfarray.make_surface(transformed)

    return cached_parquet



# Position de la caméra
view_pos = 0

# Font pour afficher le nom de la salle
font = pygame.font.SysFont("Arial", 30)

### --- BOUCLE DE JEU --- ###
while True:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Gestion du déplacement horizontal
    mouse_x, mouse_y = pygame.mouse.get_pos()
    speed_factor = 1 + (1 - PERSPECTIVE) * 2  # Rend le déplacement plus naturel
    if mouse_x < 300:
        view_pos = max(0, view_pos - (300 - mouse_x) / (10 * speed_factor))
        cached_parquet = None
    if mouse_x > W - 300:
        view_pos = min(CORRIDOR_WIDTH - W, view_pos + (mouse_x - (W - 300)) / (10 * speed_factor))
        cached_parquet = None

    # Dessin des murs et du sol
    for i in range(WALL_SIZE):
        screen.blit(wall, (-(view_pos % WALL_SIZE) + i * WALL_SIZE, 0))

    # Affichage du parquet transformé
    corridor_surface_persp = perspective_parquet(parquet,view_pos)
    screen.blit(corridor_surface_persp, (0-WALL_SIZE*PERSPECTIVE/2, WALL_SIZE), ((corridor_surface_persp.get_width()-W)//2, 0, W+WALL_SIZE*PERSPECTIVE, FLOOR_HEIGHT))

    # Affichage de la ligne entre mur et sol
    for i in range(W // WALL_SIZE + 2):
        screen.blit(wall, (-(view_pos % WALL_SIZE) + i * WALL_SIZE, 0))


    # Affichage du nom de la salle
    text = font.render("Salle des Maîtres", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    pygame.display.flip()
    clock.tick(50)