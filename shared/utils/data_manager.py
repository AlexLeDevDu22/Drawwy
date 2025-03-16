import json
import yaml
from dotenv import load_dotenv

def reload():
    global PLAYER_DATA
    global SHOP_ITEMS
    global SOLO_GAME
    global CONFIG

    with open('data/player_data.json') as f:
        PLAYER_DATA = json.load(f)
    with open('data/shop_items.json') as f:
        SHOP_ITEMS = json.load(f)
    with open('data/solo_game.json') as f:
        SOLO_GAME = json.load(f)
    with open('config.yaml') as f:
        CONFIG = yaml.safe_load(f)

def save_data(file):
    global PLAYER_DATA
    global SHOP_ITEMS
    global SOLO_GAME

    with open(f'data/{file.lower()}.json', 'w') as f:
        if file =="PLAYER_DATA":
            json.dump(PLAYER_DATA, f, ensure_ascii=False, indent=4)
        elif file =="SHOP_ITEMS":
            json.dump(SHOP_ITEMS, f, ensure_ascii=False, indent=4)
        elif file =="SOLO_GAME":
            json.dump(SOLO_GAME, f, ensure_ascii=False, indent=4)

PLAYER_DATA = {}
SHOP_ITEMS = {}
SOLO_GAME = {}
CONFIG = {}
reload()

load_dotenv()