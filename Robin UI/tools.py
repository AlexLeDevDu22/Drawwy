from sentence_transformers import SentenceTransformer, util
import json
import random
import yaml
import pygame
from pygame.locals import *
from PIL import Image, ImageFilter
info_ecran = pygame.display.Info()
largeur, hauteur = info_ecran.current_w, info_ecran.current_h
ecran = pygame.display.set_mode((largeur, hauteur))

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


def init_sentence_model():
    global model 
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # Gère plusieurs langues

def check_sentence(sentence1, sentence2):
    global model
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
def create_canvas(height, width, default_value="."):
    return [[default_value for _ in range(width)] for _ in range(height)]



def flou(pygame_surface, blur_radius=3.5):
    width, height = pygame_surface.get_size()
    image_str = pygame.image.tostring(pygame_surface, "RGBA")
    image_pil = Image.frombytes("RGBA", (width, height), image_str)
    blurred_pil = image_pil.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred_str = blurred_pil.tobytes()
    blurred_surface = pygame.image.fromstring(blurred_str, (width, height), "RGBA")
    return blurred_surface

  
dico_co={
    1: [(5.5/100*largeur,12.5/100*hauteur),(1/100*largeur, 11/100*hauteur, 18/100*largeur, 7/100*hauteur),(12/100*largeur,14/100*hauteur),(17.4/100*largeur,13.2/100*hauteur),(12/100*largeur,12/100*hauteur)],
    2: [(5.5/100*largeur,19.5/100*hauteur),(1/100*largeur, 18/100*hauteur, 18/100*largeur, 7.1/100*hauteur),(12/100*largeur,21/100*hauteur),(17.4/100*largeur,20.2/100*hauteur),(12/100*largeur,19/100*hauteur)],
    3: [(5.5/100*largeur,26.5/100*hauteur),(1/100*largeur, 25/100*hauteur, 18/100*largeur, 7/100*hauteur),(12/100*largeur,28/100*hauteur),(17.4/100*largeur,27.2/100*hauteur),(12/100*largeur,26/100*hauteur)],
    4: [(5.5/100*largeur,33.5/100*hauteur),(1/100*largeur, 32/100*hauteur, 18/100*largeur, 7/100*hauteur),(12/100*largeur,35/100*hauteur),(17.4/100*largeur,34.2/100*hauteur),(12/100*largeur,33/100*hauteur)],
    5: [(5.5/100*largeur,40.5/100*hauteur),(1/100*largeur, 39/100*hauteur, 18/100*largeur, 7/100*hauteur),(12/100*largeur,42/100*hauteur),(17.4/100*largeur,41.2/100*hauteur),(12/100*largeur,40/100*hauteur)],
    6: [(5.5/100*largeur,47.5/100*hauteur),(1/100*largeur, 46/100*hauteur, 18/100*largeur, 7/100*hauteur),(12/100*largeur,49/100*hauteur),(17.4/100*largeur,48.2/100*hauteur),(12/100*largeur,47/100*hauteur)],
    7: [(5.5/100*largeur,54.5/100*hauteur),(1/100*largeur, 53/100*hauteur, 18/100*largeur, 7.1/100*hauteur),(12/100*largeur,56/100*hauteur),(17.4/100*largeur,55.2/100*hauteur),(12/100*largeur,54/100*hauteur)],
    8: [(5.5/100*largeur,61.5/100*hauteur),(1/100*largeur, 60/100*hauteur, 18/100*largeur, 7/100*hauteur),(12/100*largeur,63/100*hauteur),(17.4/100*largeur,62.2/100*hauteur),(12/100*largeur,61/100*hauteur)],
    9: [(5.5/100*largeur,68.5/100*hauteur),(1/100*largeur, 67/100*hauteur, 18/100*largeur, 7/100*hauteur),(12/100*largeur,70/100*hauteur),(17.4/100*largeur,69.2/100*hauteur),(12/100*largeur,68/100*hauteur)]




}
def banniere(numero,pseudo,couleurs,points,trouver):
    pygame.draw.rect(ecran, couleurs,dico_co[numero][1])
    police = pygame.font.SysFont("serif " ,30)
    image_texte = police.render ( pseudo, 1 , (0,0,0) )
    police = pygame.font.SysFont("serif " ,20)
    ecran.blit(image_texte, dico_co[numero][0])
    image_texte = police.render ( "points:    "+str(points), 1 , (0,0,0) )
    ecran.blit(image_texte, dico_co[numero][2])

    image_texte = police.render ( "Trouvé ? ", 1 , (0,0,0) )
    ecran.blit(image_texte, dico_co[numero][4])
    pygame.draw.circle(ecran, NOIR, dico_co[numero][3], 7)
    if trouver == True:
        pygame.draw.circle(ecran, VERT,dico_co[numero][3], 5)
    else:
        pygame.draw.circle(ecran, ROUGE,dico_co[numero][3], 5)



