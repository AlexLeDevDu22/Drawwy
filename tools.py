from sentence_transformers import SentenceTransformer, util
import json
import random
import yaml
import pygame
from PIL import Image, ImageFilter
import gameVar


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
    
    
async def send_message(websocket, message):
    await websocket.send({"type":"guess","player_id":gameVar.PLAYER_ID, "guess":message})

async def websocket_draw(websocket, x, y, color, radius):
    # await websocket.send({"type":"draw","period":0.1,"frames":[
    #                                                         {"x":0,"y":0,"color":"#000000","width":2},
    #                                                         {"x":2,"y":1},
    #                                                         {"x":0,"y":0,"color":"#220000"},
    #                                                         {"x":2,"y":1},
    #                                                         {"x":0,"y":0,"width":3},
    #                                                         {"x":2,"y":1}
    #                                                         ]
    # })
    
    await websocket.send({"type":"draw","period":0.1,"frames":[
                                                            {"x":x,"y":y,"color":color,"radius":radius},
                                                            ]
    })

model=None
def check_sentence(sentence1, sentence2):
    global model
    if not model:
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # Gère plusieurs langues
    emb1 = model.encode(sentence1, convert_to_tensor=True)
    emb2 = model.encode(sentence2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2).item()
    return score>=config["sentence_checker_seuil"]


def draw_canvas(canvas,x,y,color,radius):
    height = len(canvas)
    width = len(canvas[0]) if height > 0 else 0

    for i in range(height):
        for j in range(width):
            # Distance au centre (x, y) pour voir si c'est dans le cercle
            if (i - y) ** 2 + (j - x) ** 2 <= radius ** 2:
                canvas[i][j] = color  # Colorier la case
                
                
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