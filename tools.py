from sentence_transformers import SentenceTransformer, util
import json
import random
import yaml
import pygame
from PIL import Image, ImageFilter
import gameVar
import time


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

def get_random_sentence():
    with open("Max/phrases_droles_v2.json") as f:
        return random.choice(json.load(f))
    
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # Gère plusieurs langues

def check_sentences(phrase1, phrase2):
    global model
    emb1 = model.encode(phrase1, convert_to_tensor=True)
    emb2 = model.encode(phrase2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2).item()
    return score>config["sentence_checker_seuil"]
    
async def send_message(websocket, message):
    await websocket.send(json.dumps({"type":"guess","player_id":gameVar.PLAYER_ID, "guess":message}))

async def websocket_draw(websocket, frames):
    #simplify frames
    
    color, radius=None, None
    for frame in frames:
        if frame["color"]==color:
            del frame["color"]
        if frame["radius"]==radius: 
            del frame["radius"]
    
    await websocket.send(json.dumps({"type":"draw","frames":frames}))

def update_canva_by_frames(frames, specified_canva=None):
    current_drawing_color=(0,0,0)
    current_drawing_radius=1
    
    for frame in frames:#draw
        time.sleep(0.45/len(frames))
        if "color" in frame.keys():
            current_drawing_color=frame["color"]
        if "radius" in frame.keys():
            current_drawing_radius=frame["radius"]
        
        if specified_canva:
            specified_canva=draw_brush_line(specified_canva, frame["x1"], frame["y1"],frame["x2"], frame["y2"], current_drawing_color, current_drawing_radius)
        else:
            gameVar.CANVAS=draw_brush_line(gameVar.CANVAS, frame["x1"], frame["y1"], frame["x2"], frame["y2"], current_drawing_color, current_drawing_radius)
        
        time.sleep(0.45/len(frames))
    
    if specified_canva:
        return specified_canva

def draw_brush_line(canvas, x1, y1, x2, y2, color, radius):
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
                        canvas[cy + j][cx + i] = color

    # Fonction pour dessiner une ligne épaisse
    def draw_thick_line(x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        dist = max(abs(dx), abs(dy))
        
        # Interpolation linéaire pour créer la ligne
        for step in range(dist + 1):
            t = step / dist
            x = round(x1 + t * dx)
            y = round(y1 + t * dy)
            draw_circle(x, y)  # On dessine un cercle autour de chaque point

    # Dessiner la ligne épaisse
    draw_thick_line(x1, y1, x2, y2)

    # Dessiner les extrémités arrondies
    draw_circle(x1, y1)
    draw_circle(x2, y2)

    return canvas  # Retourne le canvas mis à jour

                
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