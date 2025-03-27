import json
import yaml
from dotenv import load_dotenv
import pygame
from PIL import Image
import time


def reload():
    """
    Reloads and updates global data structures from various data sources.

    This function fetches and loads player data, shop items, solo themes, and 
    configuration settings from JSON and YAML files. Additionally, it processes 
    emotes from the shop items, distinguishing between image and GIF types, and 
    prepares them for use in the Pygame environment. Emote images are loaded 
    directly, while GIFs are processed into frames and their metadata is stored 
    for animation.
    """

    global PLAYER_DATA, SHOP_ITEMS, SOLO_THEMES, CONFIG, PYGAME_EMOTES

    with open('data/player_data.json', encoding="utf-8") as f:
        PLAYER_DATA = json.load(f)
    with open('data/shop/shop_items.json', encoding="utf-8") as f:
        SHOP_ITEMS = json.load(f)
    with open('data/solo_themes.json', encoding="utf-8") as f:
        SOLO_THEMES = json.load(f)
    with open('config.yaml') as f:
        CONFIG = yaml.safe_load(f)

    PYGAME_EMOTES = {
        e["index"]: e for e in SHOP_ITEMS if e["category"] == "Emotes"}
    for i in PYGAME_EMOTES.keys():
        if ".gif" not in PYGAME_EMOTES[i]["image_path"]:  # image
            PYGAME_EMOTES[i]["type"] = "image"
            PYGAME_EMOTES[i]["image_pygame"] = pygame.image.load(
                PYGAME_EMOTES[i]["image_path"])
        else:  # GIF
            gif = Image.open(PYGAME_EMOTES[i]["image_path"])

            frames = []
            for j in range(gif.n_frames):
                gif.seek(j)  # Aller à la frame i
                frame = gif.convert("RGBA").resize(
                    (150, 150))  # Redimensionne à 100x100

                # Convertir en Surface Pygame
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                pygame_frame = pygame.image.fromstring(data, size, mode)

                frames.append(pygame_frame)

            PYGAME_EMOTES[i]["type"] = "gif"
            PYGAME_EMOTES[i]["gif_frame_duration"] = gif.info["duration"] / \
                len(frames)
            PYGAME_EMOTES[i]["gif_frames"] = frames
            PYGAME_EMOTES[i]["gif_start_time"] = time.time()


def save_data(*args):
    """
    Enregistre les données dans les fichiers correspondants.

    Args:
        *args (str): noms des fichiers à enregistrer. Les seuls noms de fichiers
            acceptés sont "PLAYER_DATA" et "SOLO_THEMES".

    Raises:
        ValueError: si l'un des noms de fichiers n'est pas reconnu.
    """
    global PLAYER_DATA
    global SOLO_THEMES

    for file in args:
        with open(f'data/{file.lower()}.json', 'w', encoding="utf-8") as f:
            if file == "PLAYER_DATA":
                json.dump(PLAYER_DATA, f, ensure_ascii=False, indent=4)
            elif file == "SOLO_THEMES":
                json.dump(SOLO_THEMES, f, ensure_ascii=False, indent=4)
            else:
                print(file, " ce fichier n'est pas reconnu")
                raise ValueError

PLAYER_DATA = {}
SHOP_ITEMS = []
SOLO_THEMES = []
CONFIG = {}
PYGAME_EMOTES = {}
reload()

load_dotenv()
