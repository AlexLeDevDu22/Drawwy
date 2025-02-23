import pygame
import sys
import json
import random

with open("tests/gallery/gamery_data.json", "r") as f:
    rooms = json.load(f)


pygame.init()
screen = pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h))
W,H=screen.get_size()
clock = pygame.time.Clock()

frames_per_dimensions={(200,200):{"image": pygame.image.load("tests/gallery/assets/frame6.png"), "x": 24, "y": 39, "w": 150, "h": 129}}

# Chargement des images (remplace les chemins par tes propres assets)
wall = pygame.image.load("tests/gallery/assets/wall.jpg").convert()
line = pygame.image.load("tests/gallery/assets/line.png").convert_alpha()
parquet = pygame.image.load("tests/gallery/assets/parquet.jpg").convert()

WALL_SIZE = int(0.80*H)
LINE_SIZE = W

wall = pygame.transform.scale(wall, (WALL_SIZE, WALL_SIZE))
line = pygame.transform.scale(line, (LINE_SIZE, LINE_SIZE*0.01))
parquet = pygame.transform.rotate(parquet, 270)
parquet = pygame.transform.scale(parquet, (WALL_SIZE, WALL_SIZE*0.9))

n=0
for i in range(len(rooms)):
    for j in range(len(rooms[i]["draws"])):
        if rooms[i]["draws"][j]["path"] is not None:
            rooms[i]["draws"][j]["image"]=pygame.image.load("tests/gallery/draws/"+rooms[i]["draws"][j]["path"]).convert()
            
            image_w, image_h=rooms[i]["draws"][j]["image"].get_size()

            rooms[i]["draws"][j]["frame"]=frames_per_dimensions[(image_w,image_h)]
            rooms[i]["draws"][j]["frame"]["image"]=pygame.transform.scale(rooms[i]["draws"][j]["frame"]["image"], (image_w, image_h))

            rooms[i]["draws"][j]["image"] = pygame.transform.scale(rooms[i]["draws"][j]["image"], (rooms[i]["draws"][j]["frame"]["w"], rooms[i]["draws"][j]["frame"]["h"]))

        rooms[i]["draws"][j]["x"]=100+n*400
        rooms[i]["draws"][j]["y"]=random.randint(100,int(WALL_SIZE) - 200)

        n+=1

# Initialisation de la "caméra" ou vue
view_pos = 0

# Préparation d'une font pour afficher le nom de la salle
font = pygame.font.SysFont("Arial", 30)

while True:
    screen.fill((255,255,255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Utilisation de la souris pour définir la position de la vue
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if mouse_x<300:
        view_pos = max(0,view_pos-(300-mouse_x)/14)
    
    if mouse_x > W-300:
        view_pos = min(100+n*400  - W + 80,view_pos+(mouse_x-(W-300))/14)
    

    # Dessiner les calques avec leur décalage respectif

        
    for i in range(WALL_SIZE):
        screen.blit(wall, (-(view_pos%WALL_SIZE)+i*WALL_SIZE, 0))
        screen.blit(parquet, (-(view_pos%WALL_SIZE)+i*WALL_SIZE, WALL_SIZE))
        
    for i in range(int(W//LINE_SIZE)+2):
        screen.blit(line, (-(view_pos%LINE_SIZE)+i*LINE_SIZE, WALL_SIZE-line.get_height()//2))


    for room in rooms:
        for draw in room["draws"]:
            if draw["path"] is not None:
                image_w, image_h=draw["image"].get_size()

                screen.blit(draw["image"], (draw["x"]+draw["frame"]["x"]-view_pos, draw["y"]+draw["frame"]["y"]))
                draw["frame"]["image"].set_alpha(128)
                screen.blit(draw["frame"]["image"], (draw["x"]-view_pos, draw["y"]))

            else:
                shadow = pygame.Surface((200, 200), pygame.SRCALPHA)
                shadow.fill((0, 0, 0, 100))
                screen.blit(shadow, (draw["x"]-view_pos, draw["y"]))  # Position de la colonne

    # Afficher le nom de la salle
    text = font.render("Salle des Maîtres", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    pygame.display.flip()
    clock.tick(60)
