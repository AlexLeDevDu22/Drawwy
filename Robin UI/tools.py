from sentence_transformers import SentenceTransformer, util
import json
import random
import yaml

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