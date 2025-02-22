from sentence_transformers import SentenceTransformer, util
import json
import random
import yaml
import pygame
from PIL import Image, ImageFilter
from dotenv import load_dotenv
import gameVar
import time
from datetime import datetime
import websockets
import os
import socket

load_dotenv()

NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
BEIGE = (250, 240, 230)
VERT = (0,255,0)
ROUGE= (255,0,0)
BLEU= (0,0,255)
JAUNE=(255,255,0)
MAGENTA=(255,0,255)
CYAN=(0,255,255)



with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def is_connected():
    try:
        # Tente de se connecter à un serveur DNS public (Google)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


async def test_server():
    NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")
    try:
        async with websockets.connect("wss://"+NGROK_DOMAIN) as ws:
            return True
    except:
        return False

def get_random_sentence():
    with open("Max/phrases_droles_v2.json") as f:
        return random.choice(json.load(f))
    
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # Gère plusieurs langues

def check_sentences(phrase1, phrase2):
    global model
    emb1 = model.encode(phrase1, convert_to_tensor=True)
    emb2 = model.encode(phrase2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2).item()
    print(score)
    return score>config["sentence_checker_seuil"]
    
async def send_message(websocket, message, remaining_time):
    await websocket.send(json.dumps({"type":"guess","player_id":gameVar.PLAYER_ID, "guess":message, "remaining_time":remaining_time}))

async def websocket_draw(websocket, frames):
    #simplify frames
    
    color, radius=None, None
    for frame in frames:
        if frame["type"]=="draw":
            if frame["color"]==color:
                del frame["color"]
            if frame["radius"]==radius: 
                del frame["radius"]
    
    await websocket.send(json.dumps({"type":"draw","frames_types":"draw","frames":frames}))

def update_canva_by_frames(frames, specified_canva=None, delay=True, reset=False):
    if reset:
<<<<<<< HEAD
=======
        gameVar.ALL_FRAMES=[]
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
        if specified_canva:
            specified_canva=[[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]
        else:
            gameVar.CANVAS=[[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]
            
    current_drawing_color=(0,0,0)
    current_drawing_radius=1
    
<<<<<<< HEAD
    print(gameVar.ROLL_BACK)
    print(frames)
    new_frames=frames.copy()
    new_frames=remove_steps_by_roll_back(new_frames, gameVar.ROLL_BACK)
    print(new_frames)
    
    for frame in new_frames:#draw
        if frame["type"]=="draw":
            if delay: time.sleep(0.45/len(frames))
=======
    new_frames=frames.copy()
    print(new_frames)
    new_frames=split_steps_by_roll_back(new_frames, gameVar.ROLL_BACK)
    print(new_frames)

    for frame in new_frames[0]:#draw
        if frame["type"]=="draw":
            if delay: 
                duration=1/len(frames)
            else:
                duration=0
            
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
            if "color" in frame.keys():
                current_drawing_color=frame["color"]
            if "radius" in frame.keys():
                current_drawing_radius=frame["radius"]
            
            if specified_canva:
<<<<<<< HEAD
                specified_canva=draw_brush_line(specified_canva, frame["x1"], frame["y1"],frame["x2"], frame["y2"], current_drawing_color, current_drawing_radius)
            else:
                gameVar.CANVAS=draw_brush_line(gameVar.CANVAS, frame["x1"], frame["y1"], frame["x2"], frame["y2"], current_drawing_color, current_drawing_radius)
            
            if delay:time.sleep(0.45/len(frames))
=======
                specified_canva=draw_brush_line(specified_canva, frame["x1"], frame["y1"],frame["x2"], frame["y2"], current_drawing_color, current_drawing_radius, duration)
            else:
                gameVar.CANVAS=draw_brush_line(gameVar.CANVAS, frame["x1"], frame["y1"], frame["x2"], frame["y2"], current_drawing_color, current_drawing_radius, duration)

        gameVar.ALL_FRAMES.append(frame)

    for frame in new_frames[1]:
        gameVar.ALL_FRAMES.append(frame)
            
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
    if specified_canva:
        return specified_canva

def draw_brush_line(canvas, x1, y1, x2, y2, color, radius, duration):
    """Dessine une ligne épaisse et arrondie entre (x1, y1) et (x2, y2) directement dans canvas"""
    height = len(canvas)
    width = len(canvas[0]) if height > 0 else 0

    def in_bounds(x, y):
        """Vérifie si (x, y) est dans les limites de canvas"""
        return 0 <= x < width and 0 <= y < height

    # Fonction pour dessiner un cercle dans canvas
    radius=max(radius//4,1)
    def draw_circle(cx, cy):
        for i in range(-radius, radius):
            for j in range(-radius, radius):
                if i ** 2 + j ** 2 <= radius ** 2:  # Vérifie si (i, j) est dans le cercle
                    if in_bounds(cx + i, cy + j):
                        canvas[cy + j][cx + i] = (color[0], color[1], color[2])  # Mettre la couleur (R, G, B)

    # Fonction pour dessiner une ligne épaisse
    def draw_thick_line(x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        dist = max(abs(dx), abs(dy))
        
        # Interpolation linéaire pour créer la ligne
        step_duration=duration/dist
        for step in range(dist + 1):
            t = step / dist
            x = round(x1 + t * dx)
            y = round(y1 + t * dy)
            draw_circle(x, y)  # On dessine un cercle autour de chaque point
            
            time.sleep(max(0,step_duration-0.002))

    # Dessiner la ligne épaisse
    draw_thick_line(x1, y1, x2, y2)

    # Dessiner les extrémités arrondies
    draw_circle(x1, y1)
    draw_circle(x2, y2)

    return canvas  # Retourne le canvas mis à jour

<<<<<<< HEAD
def remove_steps_by_roll_back(frames, roll_back):
    if roll_back == 0:
        return frames  # Rien à supprimer

    new_frames = []
    removed = 0  # Nombre d'éléments supprimés

    for frame in reversed(frames):  # On parcourt à l'envers
        if removed < roll_back and frame["type"] in {"new_step", "shape"}:
            removed += 1
        else:
            new_frames.append(frame)

    return list(reversed(new_frames))  # On remet l'ordre original

=======
def split_steps_by_roll_back(frames, roll_back):
    new_frames = frames.copy()
    for i in range(len(new_frames)-1,-1,-1):  # On parcourt à l'envers

        if frames[i]["type"] in {"new_step", "shape"}:
            roll_back-=1
        if roll_back==0:
            return [new_frames[:i], new_frames[i:]]

    return [new_frames,[]]
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
                
def get_screen_size():
    info_ecran = pygame.display.Info()
    return info_ecran.current_w, info_ecran.current_h

def flou(pygame_surface, blur_radius=3.5):
    width, height = pygame_surface.get_size()
    image_str = pygame.image.tostring(pygame_surface, "RGBA")
    image_pil = Image.frombytes("RGBA", (width, height), image_str)
    blurred_pil = image_pil.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred_str = blurred_pil.tobytes()
    blurred_surface = pygame.image.fromstring(blurred_str, (width, height), "RGBA")
    return blurred_surface

<<<<<<< HEAD
def save_bmp(color_matrix, filename):
=======

def lines_return(text, font, max_largeur_pixels):
    mots = text.split()
    lignes = []
    ligne_actuelle = ""

    for mot in mots:
        # Obtenez la largeur du mot actuel en pixels
        largeur_mot = font.size(mot)[0]

        # Si la ligne actuelle + le mot ne dépasse pas la largeur maximale en pixels
        if font.size(ligne_actuelle + " " + mot if ligne_actuelle else mot)[0] <= max_largeur_pixels:
            ligne_actuelle += " " + mot if ligne_actuelle else mot
        else:
            lignes.append(ligne_actuelle)
            ligne_actuelle = mot

    if ligne_actuelle:
        lignes.append(ligne_actuelle)

    return lignes

def save_canvas(color_matrix, filename, sentence):
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
    height = len(color_matrix)
    width = max(len(row) for row in color_matrix)  # Trouve la ligne la plus longue

    img = Image.new("RGB", (width, height), "white")  # Fond blanc

    for y, row in enumerate(color_matrix):
        for x, color in enumerate(row):
            if color is not None:
<<<<<<< HEAD
                img.putpixel((x, y), (color[0], color[1], color[2]))# Mettre la couleur (R, G, B)
            else:
                img.putpixel((x,y), (255,255,255))
    img.save(filename, "BMP")
=======
                img.putpixel((x, y), (color[0], color[1], color[2]))  # Mettre la couleur (R, G, B)
            else:
                img.putpixel((x, y), (255, 255, 255))

    img.save(filename, "BMP")

    # Ajouter la phrase en fin de fichier BMP
    with open(filename, "ab") as f:
        f.write(b"\nMETADATA_START\n")  # Marqueur pour retrouver la phrase
        f.write(sentence.encode("utf-8"))  # Écriture de la phrase
        f.write(b"\nMETADATA_END\n")  # Marqueur de fin

>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
