import json
import yaml
from dotenv import load_dotenv

def reload():
    global PLAYER_DATA
    global SHOP_ITEMS
    global SOLO_THEMES
    global CONFIG

    with open('data/player_data.json') as f:
        PLAYER_DATA = json.load(f)
    with open('data/shop/shop_items.json') as f:
        SHOP_ITEMS = json.load(f)
    with open('data/solo_themes.json') as f:
        SOLO_THEMES = json.load(f)
    with open('config.yaml') as f:
        CONFIG = yaml.safe_load(f)

def save_data(file):
    global PLAYER_DATA
    global SHOP_ITEMS
    global SOLO_THEMES

    with open(f'data/{file.lower()}.json', 'w') as f:
        if file =="PLAYER_DATA":
            json.dump(PLAYER_DATA, f, ensure_ascii=False, indent=4)
        elif file =="SOLO_THEMES":
            json.dump(SOLO_THEMES, f, ensure_ascii=False, indent=4)
        else:
            print(file, " ce fichier n'est pas reconnu")
            raise ValueError

PLAYER_DATA = {}
SHOP_ITEMS = {}
SOLO_THEMES = {}
CONFIG = {}
reload()

load_dotenv()