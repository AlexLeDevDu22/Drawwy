import pygame
import sys
import json
import random
import cv2
import numpy as np

### --- CHARGEMENT DES DONNÉES --- ###

with open("tests/gallery/gamery_data.json", "r") as f:
    rooms = json.load(f)

pygame.init()
screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h))
W, H = screen.get_size()
clock = pygame.time.Clock()

frames_per_dimensions = {
    (200, 200): {
        "image": pygame.image.load("tests/gallery/assets/frame6.png"), 
        "x": 24, "y": 39, "w": 150, "h": 129
    }
}

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
CORRIDOR_WIDTH = 4*W
FLOOR_HEIGHT = int(0.9 * WALL_SIZE)

# Création de la surface sol (parquet répété)
corridor_surface = pygame.Surface((CORRIDOR_WIDTH, FLOOR_HEIGHT))
corridor_surface = corridor_surface.convert()
parquet_w, parquet_h = parquet.get_size()

for x in range(0, CORRIDOR_WIDTH, parquet_w):
    corridor_surface.blit(parquet, (x, 0))

# --- TRANSFORMATION EN PERSPECTIVE --- #
def perspective_transform(surface):
    arr = pygame.surfarray.array3d(surface)
    arr = np.transpose(arr, (1, 0, 2))
    
    h, w = arr.shape[:2]
    top_w = w * PERSPECTIVE
    dx = (w - top_w) / 2
    src_pts = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    dst_pts = np.float32([[dx, 0], [dx + top_w, 0], [0, h], [w, h]])

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    transformed = cv2.warpPerspective(arr, matrix, (w, h))
    transformed = np.transpose(transformed, (1, 0, 2))

    return pygame.surfarray.make_surface(transformed)

corridor_surface_persp = perspective_transform(corridor_surface)

# --- CHARGEMENT DES DESSINS AVEC CADRES --- #
n = 0
for i in range(len(rooms)):
    for j in range(len(rooms[i]["draws"])):
        if rooms[i]["draws"][j]["path"] is not None:
            rooms[i]["draws"][j]["image"] = pygame.image.load("tests/gallery/draws/" + rooms[i]["draws"][j]["path"]).convert()
            image_w, image_h = rooms[i]["draws"][j]["image"].get_size()
            rooms[i]["draws"][j]["frame"] = frames_per_dimensions.get((image_w, image_h))
            if rooms[i]["draws"][j]["frame"]:
                rooms[i]["draws"][j]["frame"]["image"] = pygame.transform.scale(rooms[i]["draws"][j]["frame"]["image"], (image_w, image_h))
                rooms[i]["draws"][j]["image"] = pygame.transform.scale(rooms[i]["draws"][j]["image"], (rooms[i]["draws"][j]["frame"]["w"], rooms[i]["draws"][j]["frame"]["h"]))
        
        rooms[i]["draws"][j]["x"] = 100 + n * 400
        rooms[i]["draws"][j]["y"] = random.randint(100, int(WALL_SIZE) - 200)
        n += 1

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
    if mouse_x < 300:
        view_pos = max(0, view_pos - (300 - mouse_x) / 14)
    if mouse_x > W - 300:
        view_pos = min(CORRIDOR_WIDTH - W, view_pos + (mouse_x - (W - 300)) / 14)

    # Dessin des murs et du sol
    for i in range(WALL_SIZE):
        screen.blit(wall, (-(view_pos % WALL_SIZE) + i * WALL_SIZE, 0))

    # Affichage du parquet transformé
    screen.blit(corridor_surface_persp, (0, WALL_SIZE), area=pygame.Rect(view_pos, 0, W, FLOOR_HEIGHT))

    # Affichage de la ligne entre mur et sol
    for i in range(int(W // LINE_SIZE) + 2):
        screen.blit(line, (-(view_pos % LINE_SIZE) + i * LINE_SIZE, WALL_SIZE - line.get_height() // 2))

    # Affichage des œuvres
    for room in rooms:
        for draw in room["draws"]:
            if draw["path"] is not None:
                image_w, image_h = draw["image"].get_size()
                screen.blit(draw["image"], (draw["x"] + draw["frame"]["x"] - view_pos, draw["y"] + draw["frame"]["y"]))
                draw["frame"]["image"].set_alpha(128)
                screen.blit(draw["frame"]["image"], (draw["x"] - view_pos, draw["y"]))
            else:
                shadow = pygame.Surface((200, 200), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 100))
                screen.blit(shadow, (draw["x"] - view_pos, draw["y"]))

    # Affichage du nom de la salle
    text = font.render("Salle des Maîtres", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    pygame.display.flip()
    clock.tick(60)
