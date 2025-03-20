from sentence_transformers import SentenceTransformer, util
import json
import random
import yaml
import pygame
from PIL import Image, ImageFilter
from dotenv import load_dotenv
import MultiGame
import time
from datetime import datetime
import socketio
import os
import socket
import asyncio

load_dotenv()

NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
BEIGE = (250, 240, 230)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)
BLEU = (0, 0, 255)
JAUNE = (255, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)


with open("assets/config.yaml", "r") as f:
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
        sio = socketio.AsyncClient()
        await sio.connect(f"https://{NGROK_DOMAIN}")
        return True
    except BaseException:
        return False

asyncio.run(test_server())


def load_bmp_to_matrix(file_path):
    """Charge une image BMP et retourne une matrice de pixels."""
    # Charger l'image avec Pygame
    image = pygame.image.load(file_path).convert()
    width, height = image.get_size()

    # Extraire chaque pixel dans une matrice
    pixel_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            color = image.get_at((x, y))  # Obtenir la couleur du pixel (x, y)
            row.append((color.r, color.g, color.b))  # Ajouter (R, G, B)
        pixel_matrix.append(row)

    return pixel_matrix


def matrix_to_image(pixel_matrix):
    """Affiche une matrice de pixels sur une surface Pygame."""
    width = len(pixel_matrix[0])  # Largeur de la matrice
    height = len(pixel_matrix)  # Hauteur de la matrice

    # Créer une Surface avec un canal alpha pour la transparence
    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    for y in range(height):
        for x in range(width):
            # Récupérer la couleur RGBA (incluant alpha si besoin)
            color = pixel_matrix[y][x]
            surface.set_at((x, y), color)  # Définir le pixel sur la surface

    return surface


def apply_circular_mask(image):
    """Applique un masque circulaire avec transparence à une image Pygame."""
    # Créer un masque avec canal alpha
    mask = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))  # Transparence totale

    # Dessiner un cercle blanc opaque dans le masque
    pygame.draw.circle(
        mask,
        (255, 255, 255, 255),  # Blanc opaque
        (image.get_width() // 2, image.get_height() // 2),
        image.get_width() // 2,
    )

    # Appliquer le masque sur l'image
    image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def get_random_sentence():
    with open("Max/phrases_droles_v2.json") as f:
        return random.choice(json.load(f))


model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2")  # Gère plusieurs langues


def check_sentences(phrase1, phrase2):
    global model
    emb1 = model.encode(phrase1, convert_to_tensor=True)
    emb2 = model.encode(phrase2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2).item()
    print(score)
    return score > config["sentence_checker_seuil"]


def emit_sio(sio, event, data):
    try:
        loop = asyncio.get_running_loop()  # Essaie d'obtenir une boucle existante
        # Crée une tâche si la boucle existe
        loop.create_task(sio.emit(event, data))
    except RuntimeError:
        # Créer une nouvelle boucle si aucune n'existe
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Exécuter directement l'événement
        loop.run_until_complete(sio.emit(event, data))


def simplify_frames(frames):

    color, radius = None, None
    for i in range(len(frames)):
        if frames[i]["type"] == "line":
            if frames[i]["color"] == color:
                del frames[i]["color"]
            if frames[i]["radius"] == radius:
                del frames[i]["radius"]
    return frames


def update_canva_by_frames(
        frames,
        specified_canva=None,
        delay=True,
        reset=False):
    if reset:
        MultiGame.ALL_FRAMES = []
        if specified_canva:
            specified_canva = [[None for _ in range(
                config["canvas_width"])] for _ in range(config["canvas_height"])]
        else:
            MultiGame.CANVAS = [[None for _ in range(
                config["canvas_width"])] for _ in range(config["canvas_height"])]

    current_drawing_color = (0, 0, 0)
    current_drawing_radius = 1

    new_frames = frames.copy()
    new_frames = split_steps_by_roll_back(new_frames, MultiGame.ROLL_BACK)

    for frame in new_frames[0]:  # draw
        if frame["type"] == "line":
            if delay:
                duration = 1 / len(frames)
            else:
                duration = 0

            if "color" in frame.keys():
                current_drawing_color = frame["color"]
            if "radius" in frame.keys():
                current_drawing_radius = frame["radius"]

            if specified_canva:
                specified_canva = draw_brush_line(
                    specified_canva,
                    frame["x1"],
                    frame["y1"],
                    frame["x2"],
                    frame["y2"],
                    current_drawing_color,
                    current_drawing_radius,
                    duration)
            else:
                MultiGame.CANVAS = draw_brush_line(
                    MultiGame.CANVAS,
                    frame["x1"],
                    frame["y1"],
                    frame["x2"],
                    frame["y2"],
                    current_drawing_color,
                    current_drawing_radius,
                    duration)

        MultiGame.ALL_FRAMES.append(frame)

    for frame in new_frames[1]:
        MultiGame.ALL_FRAMES.append(frame)

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
    radius = max(radius // 4, 1)

    def draw_circle(cx, cy):
        for i in range(-radius, radius):
            for j in range(-radius, radius):
                if i ** 2 + \
                        j ** 2 <= radius ** 2:  # Vérifie si (i, j) est dans le cercle
                    if in_bounds(cx + i, cy + j):
                        # Mettre la couleur (R, G, B)
                        canvas[cy + j][cx + i] = (color[0], color[1], color[2])

    # Fonction pour dessiner une ligne épaisse
    def draw_thick_line(x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        dist = max(abs(dx), abs(dy))

        # Interpolation linéaire pour créer la ligne
        if dist > 0:
            step_duration = duration / dist
            for step in range(dist + 1):
                t = step / dist
                x = round(x1 + t * dx)
                y = round(y1 + t * dy)
                # On dessine un cercle autour de chaque point
                draw_circle(x, y)

                time.sleep(max(0, step_duration - 0.004))

    # Dessiner la ligne épaisse
    draw_thick_line(x1, y1, x2, y2)

    # Dessiner les extrémités arrondies
    draw_circle(x1, y1)
    draw_circle(x2, y2)

    return canvas  # Retourne le canvas mis à jour


def split_steps_by_roll_back(frames, roll_back):
    new_frames = frames.copy()
    for i in range(len(new_frames) - 1, -1, -1):  # On parcourt à l'envers

        if frames[i]["type"] in {"new_step", "shape"}:
            roll_back -= 1
        if roll_back == 0:
            return [new_frames[:i], new_frames[i:]]

    return [new_frames, []]


def get_screen_size():
    info_ecran = pygame.display.Info()
    return info_ecran.current_w, info_ecran.current_h


def flou(pygame_surface, blur_radius=3.5):
    width, height = pygame_surface.get_size()
    image_str = pygame.image.tostring(pygame_surface, "RGBA")
    image_pil = Image.frombytes("RGBA", (width, height), image_str)
    blurred_pil = image_pil.filter(
        ImageFilter.GaussianBlur(
            radius=blur_radius))
    blurred_str = blurred_pil.tobytes()
    blurred_surface = pygame.image.fromstring(
        blurred_str, (width, height), "RGBA")
    return blurred_surface


def lines_return(text, font, max_largeur_pixels):
    mots = text.split()
    lignes = []
    ligne_actuelle = ""

    for mot in mots:
        # Obtenez la largeur du mot actuel en pixels
        largeur_mot = font.size(mot)[0]

        # Si la ligne actuelle + le mot ne dépasse pas la largeur maximale en
        # pixels
        if font.size(
            ligne_actuelle +
            " " +
                mot if ligne_actuelle else mot)[0] <= max_largeur_pixels:
            ligne_actuelle += " " + mot if ligne_actuelle else mot
        else:
            lignes.append(ligne_actuelle)
            ligne_actuelle = mot

    if ligne_actuelle:
        lignes.append(ligne_actuelle)

    return lignes


def save_canvas(color_matrix, filename, sentence):
    height = len(color_matrix)
    # Trouve la ligne la plus longue
    width = max(len(row) for row in color_matrix)

    img = Image.new("RGB", (width, height), "white")  # Fond blanc

    for y, row in enumerate(color_matrix):
        for x, color in enumerate(row):
            if color is not None:
                # Mettre la couleur (R, G, B)
                img.putpixel((x, y), (color[0], color[1], color[2]))
            else:
                img.putpixel((x, y), (255, 255, 255))

    img.save(filename, "BMP")

    # Ajouter la phrase en fin de fichier BMP
    with open(filename, "ab") as f:
        f.write(b"\nMETADATA_START\n")  # Marqueur pour retrouver la phrase
        f.write(sentence.encode("utf-8"))  # Écriture de la phrase
        f.write(b"\nMETADATA_END\n")  # Marqueur de fin
