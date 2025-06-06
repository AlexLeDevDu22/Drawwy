from sentence_transformers import SentenceTransformer, util
from shared.utils.data_manager import *
from shared.ui.common_ui import *
import pygame
from PIL import Image, ImageFilter
import time
import requests
import socket
import asyncio


def test_server(server_name):
    """
    Vérifie si le serveur MultiGame est disponible.

    :param str server_name: Le nom du serveur à tester.
    :return: True si le serveur est disponible, False sinon.
    """
    try:
        return requests.get(
            f"https://{
                CONFIG['servers'][server_name]['domain']}/num_players",
            timeout=4).status_code == 200
    except BaseException:
        return False


def load_bmp_to_matrix(file_path):
    """
    Charge une image .BMP et la convertit en une matrice de pixels.

    :param str file_path: Chemin absolu vers l'image .BMP à charger.
    :return: Une matrice de pixels (RGB) de l'image.
    :rtype: list[list[tuple[int, int, int]]]
    """
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
    """
    Convertit une matrice de pixels en une image Pygame Surface.

    :param list[list[tuple[int, int, int]]] pixel_matrix: Une matrice de pixels RGB ou RGBA.
    :return: Une Surface Pygame représentant l'image.
    :rtype: pygame.Surface
    """
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


model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2")  # Gère plusieurs langues


def check_sentences(phrase1, phrase2):
    """
    Vérifie si deux phrases sont similaires.

    :param str phrase1: Première phrase.
    :param str phrase2: Seconde phrase.
    :return: True si les phrases sont similaires, False sinon.
    :rtype: bool

    La similitude est déterminée en fonction de la valeur de configuration
    ``sentence_checker_seuil``. La fonction utilise le modèle de langage
    ``paraphrase-multilingual-MiniLM-L12-v2`` pour calculer la similarité
    entre les deux phrases.
    """
    global model
    emb1 = model.encode(phrase1, convert_to_tensor=True)
    emb2 = model.encode(phrase2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2).item()
    return score > CONFIG["sentence_checker_seuil"]


def send_ws(ws, data):
    if ws:
        try:
            loop = asyncio.get_running_loop()  # Essaie d'obtenir une boucle existante
        except RuntimeError:
            loop = asyncio.new_event_loop()  # Crée une nouvelle boucle si aucune n'existe
            asyncio.set_event_loop(loop)
        asyncio.run(ws.send(json.dumps(data)))


def simplify_frames(frames):

    color, radius = None, None
    for i in range(len(frames)):
        if frames[i]["type"] == "line":
            if frames[i]["color"] == color:
                del frames[i]["color"]
            if frames[i]["radius"] == radius:
                del frames[i]["radius"]
    return frames


def update_canva_by_frames(MultiGame, frames, delay=True, reset=False):
    if reset:
        MultiGame.ALL_FRAMES = []
        MultiGame.CANVAS = pygame.Surface(
            (MultiGame.canvas_rect.width, MultiGame.canvas_rect.height))
        MultiGame.CANVAS.fill((255, 255, 255))

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

            MultiGame.CANVAS = draw_brush_line(
                MultiGame.CANVAS,
                frame["x1"] * MultiGame.pixel_size,
                frame["y1"] * MultiGame.pixel_size,
                frame["x2"] * MultiGame.pixel_size,
                frame["y2"] * MultiGame.pixel_size,
                current_drawing_color,
                current_drawing_radius * MultiGame.pixel_size // 4)
            time.sleep(duration)

        MultiGame.ALL_FRAMES.append(frame)

    for frame in new_frames[1]:
        MultiGame.ALL_FRAMES.append(frame)


def draw_brush_line(canvas, x1, y1, x2, y2, color, radius):
    """Dessine une ligne épaisse et arrondie entre (x1, y1) et (x2, y2) directement dans canvas"""
    # Fonction pour dessiner un cercle dans canvas
    # Dessiner la ligne épaisse
    pygame.draw.line(canvas, color, (x1, y1), (x2, y2), radius * 2)

    # Dessiner les extrémités arrondies
    pygame.draw.circle(canvas, color, (x1, y1), radius)
    pygame.draw.circle(canvas, color, (x2, y2), radius)

    # achievement
    if not PLAYER_DATA["achievements"][0]["succeed"]:
        PLAYER_DATA["achievements"][0]["succeed"] = True
        save_data("PLAYER_DATA")

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


def save_canvas(surface, filename, sentence, is_pygame_surface=False):
    """Sauvegarde une surface Pygame ou une matrice de couleurs en image BMP et ajoute une phrase en métadonnées."""

    if is_pygame_surface:
        # Surface Pygame -> Extraire les dimensions et les pixels
        width, height = surface.get_size()
        img = Image.new("RGB", (width, height), "white")

        for y in range(height):
            for x in range(width):
                img.putpixel(
                    (x, y), surface.get_at(
                        (x, y))[
                        :3])  # Ignorer l'alpha

    else:
        # Matrice de couleurs -> Convertir en image
        height = len(surface)
        width = max(len(row) for row in surface)
        img = Image.new("RGB", (width, height), "white")

        for y, row in enumerate(surface):
            for x, color in enumerate(row):
                if color is not None:
                    # Mettre la couleur (R, G, B)
                    img.putpixel((x, y), (color[0], color[1], color[2]))
                else:
                    img.putpixel((x, y), (255, 255, 255))

    # Sauvegarder l'image
    img.save(filename, "BMP")

    # Ajouter la phrase en fin de fichier BMP
    with open(filename, "ab") as f:
        f.write(b"\nMETADATA_START\n")  # Marqueur pour retrouver la phrase
        f.write(sentence.encode("utf-8"))  # Écriture de la phrase
        f.write(b"\nMETADATA_END\n")  # Marqueur de fin
