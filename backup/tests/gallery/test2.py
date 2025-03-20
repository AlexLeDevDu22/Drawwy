import pygame
import sys
import json
import cv2
import numpy as np
import threading

### --- CHARGEMENT DES DONNÉES --- ###
with open("tests/gallery/gallery_data.json", "r") as f:
    rooms = json.load(f)

pygame.init()
screen = pygame.display.set_mode(
    (pygame.display.Info().current_w,
     pygame.display.Info().current_h))
W, H = screen.get_size()
clock = pygame.time.Clock()

# --- PAGE DE CHARGEMENT --- #
font = pygame.font.SysFont("Arial", 50)

# --- CHARGEMENT DES ASSETS --- #
wall = pygame.image.load("tests/gallery/assets/wall3.jpg").convert()
line = pygame.image.load("tests/gallery/assets/line.png").convert_alpha()
parquet = pygame.image.load("tests/gallery/assets/parquet.jpg").convert()

WALL_SIZE = int(0.8 * H)
LINE_SIZE = W
PERSPECTIVE = 0.6

wall = pygame.transform.scale(wall, (WALL_SIZE, WALL_SIZE))
line = pygame.transform.scale(line, (LINE_SIZE, int(LINE_SIZE * 0.01)))
parquet = pygame.transform.scale(
    parquet, (WALL_SIZE, int((H - WALL_SIZE) * (1 / PERSPECTIVE))))

# Largeur totale du sol pour permettre le déplacement
CORRIDOR_WIDTH = int(W + PERSPECTIVE * 2 * W)
FLOOR_HEIGHT = int(0.9 * WALL_SIZE)

# Liste des perspectives précalculées
cached_perspectives = []
loading_done = False
progress = 0  # Variable partagée pour la barre de chargement


def precalculate_parquet_perspectives():
    """Pré-calcul des différentes versions du sol en perspective."""
    global cached_perspectives, loading_done, progress
    for offset in range(WALL_SIZE):
        surface = pygame.Surface((CORRIDOR_WIDTH, FLOOR_HEIGHT)).convert()

        # Remplissage du sol avec le parquet
        for x in range(0, CORRIDOR_WIDTH, parquet.get_width()):
            surface.blit(parquet, (x, 0))

        # Décalage horizontal
        new_surface = pygame.Surface((surface.get_width(), FLOOR_HEIGHT))
        new_surface.blit(surface, (-offset, 0),
                         (0, 0, surface.get_width() - offset, FLOOR_HEIGHT))

        # Transformation en perspective
        arr = pygame.surfarray.array3d(new_surface)
        arr = np.transpose(arr, (1, 0, 2))
        h, w = arr.shape[:2]

        top_w = w * PERSPECTIVE
        dx = (w - top_w) / 2
        src_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        dst_pts = np.float32([[dx, 0], [dx + top_w, 0], [0, h], [w, h]])

        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        transformed = cv2.warpPerspective(arr, matrix, (w, h))
        transformed = np.transpose(transformed, (1, 0, 2))

        cached_perspectives.append(pygame.surfarray.make_surface(transformed))

        # Mettre à jour la progression (mais PAS pygame.display.flip() ici)
        progress = offset + 1

    loading_done = True


# Lancer le calcul en arrière-plan
loading_thread = threading.Thread(target=precalculate_parquet_perspectives)
loading_thread.start()

# --- BOUCLE D'ATTENTE DU CHARGEMENT --- #
while not loading_done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((0, 0, 0))  # Fond noir
    loading_text = font.render(
        f"Chargement... {progress}/{WALL_SIZE}", True, (255, 255, 255))
    bar_width = int((progress / WALL_SIZE) * W)  # Barre de progression
    pygame.draw.rect(screen, (255, 255, 255), (50, H // 2 + 50, bar_width, 20))

    screen.blit(loading_text, (W // 2 - loading_text.get_width() // 2, H // 2))
    pygame.display.flip()  # Met à jour l'affichage
    clock.tick(30)  # Éviter une boucle trop rapide

# --- CHARGEMENT TERMINÉ : ON DÉMARRE LE JEU --- #

view_pos = 0
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
    speed_factor = 1 + (1 - PERSPECTIVE) * 2
    if mouse_x < 300:
        view_pos = max(0, view_pos - (300 - mouse_x) / (10 * speed_factor))
    if mouse_x > W - 300:
        view_pos = min(CORRIDOR_WIDTH - W, view_pos +
                       (mouse_x - (W - 300)) / (10 * speed_factor))

    # Dessin des murs
    for i in range(W // WALL_SIZE + 2):
        screen.blit(wall, (-(view_pos % WALL_SIZE) + i * WALL_SIZE, 0))

    # Sélection de la bonne version pré-calculée du parquet
    corridor_surface_persp = cached_perspectives[int(view_pos) % WALL_SIZE]
    screen.blit(corridor_surface_persp,
                (-WALL_SIZE * PERSPECTIVE / 2,
                 WALL_SIZE),
                ((corridor_surface_persp.get_width() - W) // 2,
                 0,
                 W + int(WALL_SIZE * PERSPECTIVE),
                 FLOOR_HEIGHT))

    # Affichage de la ligne entre mur et sol
    for i in range(W // WALL_SIZE + 2):
        screen.blit(line, (-(view_pos % LINE_SIZE) + i *
                    LINE_SIZE, WALL_SIZE - line.get_height() // 2))

    # Affichage du nom de la salle
    text = font.render("Salle des Maîtres", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    pygame.display.flip()
    clock.tick(50)
