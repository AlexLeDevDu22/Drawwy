from shared.common_ui import *
from shared.common_utils import draw_text
from shared.tools import generate_particles

import pygame
import math
import random
import json
import os
particles = []


def show_shop(screen, W, H, mouse_pos, mouse_click):
    """Affiche l'interface de la boutique des objets de décoration"""
    # Panneau principal (effet papier)
    main_panel_width = 900
    main_panel_height = 750
    main_panel_x = (W - main_panel_width) // 2
    main_panel_y = (H - main_panel_height) // 2
    
    # Ombre du panneau
    pygame.draw.rect(screen, DARK_BEIGE, 
                    (main_panel_x + 15, main_panel_y + 15, 
                    main_panel_width, main_panel_height), 
                    border_radius=40)
    
    # Panneau principal
    pygame.draw.rect(screen, BEIGE, 
                    (main_panel_x, main_panel_y, 
                    main_panel_width, main_panel_height), 
                    border_radius=40)
    
    # Texture du papier (points aléatoires)
    for _ in range(500):
        px = random.randint(main_panel_x, main_panel_x + main_panel_width)
        py = random.randint(main_panel_y, main_panel_y + main_panel_height)
        if (px - main_panel_x - main_panel_width//2)**2 + (py - main_panel_y - main_panel_height//2)**2 <= (main_panel_width//2)**2:
            color_variation = random.randint(-15, 5)
            point_color = (
                min(255, max(0, BEIGE[0] + color_variation)),
                min(255, max(0, BEIGE[1] + color_variation)),
                min(255, max(0, BEIGE[2] + color_variation))
            )
            pygame.draw.circle(screen, point_color, (px, py), 1)
    
    # Titre
    draw_text("BOUTIQUE", TITLE_FONT, GRAY, screen, 
            W // 2 + 4, main_panel_y + 80 + 4)
    draw_text("BOUTIQUE", TITLE_FONT, BLACK, screen, 
            W // 2, main_panel_y + 80)
    
    # Charger les données
    items = load_items()
    player_data = load_player_data()
    coins = player_data.get("coins", 0)
    
    # Afficher le solde
    coin_icon = pygame.image.load("assets/icon_coin.png")
    coin_icon = pygame.transform.scale(coin_icon, (40, 40))
    coin_icon_rect = coin_icon.get_rect(center=(main_panel_x + main_panel_width - 180, main_panel_y + 80))
    screen.blit(coin_icon, coin_icon_rect)
    
    draw_text(f"{coins}", MEDIUM_FONT, BLACK, screen, 
            main_panel_x + main_panel_width - 120, main_panel_y + 80)
    
    # Variables statiques pour la pagination et filtrage
    # Utiliser un dictionnaire pour stocker l'état entre les appels
    if not hasattr(show_shop, "state"):
        show_shop.state = {
            "current_page": 0,
            "selected_category": "tous",
            "selection_mode": False
        }
    
    items_per_page = 4
    categories = ["tous"] + list(set(item["category"] for item in items))
    
    # Dessiner les onglets de catégories
    tab_width = 140
    tab_height = 50
    tab_margin = 10
    start_x = main_panel_x + (main_panel_width - (len(categories) * (tab_width + tab_margin) - tab_margin)) // 2
    
    for i, category in enumerate(categories):
        tab_x = start_x + i * (tab_width + tab_margin)
        tab_y = main_panel_y + 140
        
        # Animation de survol
        hover = tab_x <= mouse_pos[0] <= tab_x + tab_width and tab_y <= mouse_pos[1] <= tab_y + tab_height
        
        # Couleur de fond basée sur sélection/survol
        if category == show_shop.state["selected_category"]:
            tab_color = SOFT_ORANGE
        else:
            tab_color = ORANGE if hover else LIGHT_ORANGE
        
        # Dessiner l'ombre du tab
        pygame.draw.rect(screen, DARK_BEIGE,
                        (tab_x + 4, tab_y + 4, tab_width, tab_height),
                        border_radius=25)
        
        # Dessiner le tab
        pygame.draw.rect(screen, tab_color,
                        (tab_x, tab_y, tab_width, tab_height),
                        border_radius=25)
        
        # Texte du tab
        draw_text(category.upper(), SMALL_FONT, BLACK, screen,
                tab_x + tab_width // 2, tab_y + tab_height // 2)
        
        # Gestion des clics sur tab
        if mouse_click and hover:
            show_shop.state["selected_category"] = category
            show_shop.state["current_page"] = 0
            particles += generate_particles(10, tab_x, tab_y, tab_x + tab_width, tab_y + tab_height)
    
    # Bouton mode (sélection/achat)
    mode_width = 160
    mode_height = 50
    mode_x = main_panel_x + main_panel_width - mode_width - 40
    mode_y = main_panel_y + 140
    
    # Animation de survol
    hover_mode = mode_x <= mouse_pos[0] <= mode_x + mode_width and mode_y <= mouse_pos[1] <= mode_y + mode_height
    
    # Couleur basée sur mode actuel et survol
    if show_shop.state["selection_mode"]:
        mode_color = (100, 200, 100) if not hover_mode else (120, 220, 120)
        mode_text = "SÉLECTION"
    else:
        mode_color = (200, 100, 100) if not hover_mode else (220, 120, 120)
        mode_text = "ACHAT"
    
    # Dessiner l'ombre du bouton
    pygame.draw.rect(screen, DARK_BEIGE,
                    (mode_x + 4, mode_y + 4, mode_width, mode_height),
                    border_radius=25)
    
    # Dessiner le bouton
    pygame.draw.rect(screen, mode_color,
                    (mode_x, mode_y, mode_width, mode_height),
                    border_radius=25)
    
    # Texte du bouton
    draw_text(mode_text, SMALL_FONT, BLACK, screen,
            mode_x + mode_width // 2, mode_y + mode_height // 2)
    
    # Gestion des clics sur le bouton de mode
    if mouse_click and hover_mode:
        show_shop.state["selection_mode"] = not show_shop.state["selection_mode"]
        particles += generate_particles(10, mode_x, mode_y, mode_x + mode_width, mode_y + mode_height)
    
    # Filtrer les items selon la catégorie sélectionnée
    filtered_items = [item for item in items if show_shop.state["selected_category"] == "tous" or item["category"] == show_shop.state["selected_category"]]
    
    # Calculer le nombre total de pages
    total_pages = max(1, (len(filtered_items) - 1) // items_per_page + 1)
    
    # Limiter la page courante
    show_shop.state["current_page"] = min(show_shop.state["current_page"], total_pages - 1)
    
    # Afficher les items
    start_idx = show_shop.state["current_page"] * items_per_page
    item_width = 380
    item_height = 180
    item_margin = 30
    
    for i in range(min(items_per_page, len(filtered_items) - start_idx)):
        item = filtered_items[start_idx + i]
        item_x = main_panel_x + (i % 2) * (item_width + item_margin) + 70
        item_y = main_panel_y + 220 + (i // 2) * (item_height + item_margin)
        
        # Animation de survol
        hover_item = item_x <= mouse_pos[0] <= item_x + item_width and item_y <= mouse_pos[1] <= item_y + item_height
        
        # Couleur de fond basée sur sélection/achat/survol
        if item["purchased"] and item["selected"]:
            item_color = (220, 250, 220)
        else:
            item_color = LIGHT_BEIGE if hover_item else BEIGE
        
        # Ombre de l'item
        pygame.draw.rect(screen, DARK_BEIGE,
                        (item_x + 4, item_y + 4, item_width, item_height),
                        border_radius=20)
        
        # Fond de l'item
        pygame.draw.rect(screen, item_color,
                        (item_x, item_y, item_width, item_height),
                        border_radius=20)
        
        # Image de l'item
        try:
            item_img = pygame.image.load(item["image_path"])
            item_img = pygame.transform.scale(item_img, (100, 100))
        except:
            # Image de remplacement si non trouvée
            item_img = pygame.Surface((100, 100))
            item_img.fill((200, 200, 200))
        
        img_rect = item_img.get_rect(center=(item_x + 70, item_y + item_height // 2))
        screen.blit(item_img, img_rect)
        
        # Nom de l'item
        draw_text(item["name"], MEDIUM_FONT, BLACK, screen,
                item_x + 220, item_y + 40)
        
        # Description de l'item
        draw_text(item["description"], VERY_SMALL_FONT, GRAY, screen,
                item_x + 240, item_y + 80)
        
        # Prix ou statut
        if item["purchased"]:
            status_text = "SÉLECTIONNÉ" if item["selected"] else "ACHETÉ"
            status_color = (50, 150, 50) if item["selected"] else (100, 100, 100)
            draw_text(status_text, SMALL_FONT, status_color, screen,
                    item_x + 220, item_y + 130)
        else:
            price_color = (0, 100, 0) if coins >= item["price"] else (150, 0, 0)
            draw_text(f"{item['price']} pièces", SMALL_FONT, price_color, screen,
                    item_x + 220, item_y + 130)
        
        # Gestion des clics sur les items
        if mouse_click and hover_item:
            particles += generate_particles(15, item_x, item_y, item_x + item_width, item_y + item_height)
            
            if show_shop.state["selection_mode"]:
                if item["purchased"]:
                    # Basculer la sélection
                    item["selected"] = not item["selected"]
                    if item["selected"]:
                        if item["id"] not in player_data.get("selected_items", []):
                            player_data.setdefault("selected_items", []).append(item["id"])
                    else:
                        if item["id"] in player_data.get("selected_items", []):
                            player_data["selected_items"].remove(item["id"])
                    save_player_data(player_data)
                    save_items(items)
            else:
                # Mode achat
                if not item["purchased"] and coins >= item["price"]:
                    coins -= item["price"]
                    item["purchased"] = True
                    player_data["coins"] = coins
                    save_items(items)
                    save_player_data(player_data)
    
    # Boutons de pagination
    if total_pages > 1:
        nav_width = 60
        nav_height = 60
        prev_x = main_panel_x + main_panel_width // 2 - nav_width - 20
        next_x = main_panel_x + main_panel_width // 2 + 20
        nav_y = main_panel_y + main_panel_height - 100
        
        # Bouton précédent
        prev_hover = prev_x <= mouse_pos[0] <= prev_x + nav_width and nav_y <= mouse_pos[1] <= nav_y + nav_height
        prev_color = SOFT_ORANGE if prev_hover else ORANGE
        
        if show_shop.state["current_page"] > 0:
            # Ombre
            pygame.draw.circle(screen, DARK_BEIGE, (prev_x + nav_width // 2 + 4, nav_y + nav_height // 2 + 4), nav_width // 2)
            # Cercle
            pygame.draw.circle(screen, prev_color, (prev_x + nav_width // 2, nav_y + nav_height // 2), nav_width // 2)
            # Flèche
            draw_text("←", MEDIUM_FONT, BLACK, screen, prev_x + nav_width // 2, nav_y + nav_height // 2)
            
            if mouse_click and prev_hover:
                show_shop.state["current_page"] -= 1
                particles += generate_particles(10, prev_x, nav_y, prev_x + nav_width, nav_y + nav_height)
        
        # Bouton suivant
        next_hover = next_x <= mouse_pos[0] <= next_x + nav_width and nav_y <= mouse_pos[1] <= nav_y + nav_height
        next_color = SOFT_ORANGE if next_hover else ORANGE
        
        if show_shop.state["current_page"] < total_pages - 1:
            # Ombre
            pygame.draw.circle(screen, DARK_BEIGE, (next_x + nav_width // 2 + 4, nav_y + nav_height // 2 + 4), nav_width // 2)
            # Cercle
            pygame.draw.circle(screen, next_color, (next_x + nav_width // 2, nav_y + nav_height // 2), nav_width // 2)
            # Flèche
            draw_text("→", MEDIUM_FONT, BLACK, screen, next_x + nav_width // 2, nav_y + nav_height // 2)
            
            if mouse_click and next_hover:
                show_shop.state["current_page"] += 1
                particles += generate_particles(10, next_x, nav_y, next_x + nav_width, nav_y + nav_height)
        
        # Afficher numéro de page
        draw_text(f"Page {show_shop.state['current_page'] + 1}/{total_pages}", SMALL_FONT, BLACK, screen,
                main_panel_x + main_panel_width // 2, nav_y + nav_height + 30)
    
    # Bouton retour
    back_width = 180
    back_height = 60
    back_x = main_panel_x + 50
    back_y = main_panel_y + main_panel_height - 100
    
    # Animation de survol
    hover_back = back_x <= mouse_pos[0] <= back_x + back_width and back_y <= mouse_pos[1] <= back_y + back_height
    
    # Ombre du bouton
    pygame.draw.rect(screen, DARK_BEIGE,
                    (back_x + 4, back_y + 4, back_width, back_height),
                    border_radius=30)
    
    # Dessiner le bouton
    pygame.draw.rect(screen, SOFT_ORANGE if hover_back else ORANGE,
                    (back_x, back_y, back_width, back_height),
                    border_radius=30)
    
    # Texte du bouton
    draw_text("RETOUR", MEDIUM_FONT, BLACK, screen,
            back_x + back_width // 2, back_y + back_height // 2)
    
    # Gestion du clic sur le bouton retour
    if mouse_click and hover_back:
        particles += generate_particles(15, back_x, back_y, back_x + back_width, back_y + back_height)
        return screen, "home", particles
    
    # Effets de particules lors du clic
    if mouse_click:
        particles += generate_particles(10, mouse_pos[0] - 20, mouse_pos[1] - 20, mouse_pos[0] + 20, mouse_pos[1] + 20)
    
    return screen, "shop"

def load_items():
    """Charge les objets de décoration depuis un fichier JSON ou crée des objets par défaut"""
    if os.path.exists("data/shop_items.json"):
        try:
            with open("data/shop_items.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Erreur lors du chargement des items: {e}")
    
    # Items par défaut si le fichier n'existe pas
    default_items = [
        {
            "id": 1,
            "name": "Étoile Rose",
            "price": 100,
            "description": "Une jolie étoile rose",
            "image_path": "assets/decorations/star_pink.png",
            "category": "stars",
            "purchased": False,
            "selected": False
        },
        {
            "id": 2,
            "name": "Nuage Bleu",
            "price": 150,
            "description": "Un nuage bleu ciel",
            "image_path": "assets/decorations/cloud_blue.png",
            "category": "clouds",
            "purchased": False,
            "selected": False
        },
        {
            "id": 3,
            "name": "Fleur Jaune",
            "price": 200,
            "description": "Une fleur jaune lumineuse",
            "image_path": "assets/decorations/flower_yellow.png",
            "category": "flowers",
            "purchased": False,
            "selected": False
        },
        {
            "id": 4,
            "name": "Cœur Rouge",
            "price": 120,
            "description": "Un cœur rouge brillant",
            "image_path": "assets/decorations/heart_red.png",
            "category": "hearts",
            "purchased": False,
            "selected": False
        },
        {
            "id": 5,
            "name": "Étoile Verte",
            "price": 100,
            "description": "Une étoile verte scintillante",
            "image_path": "assets/decorations/star_green.png",
            "category": "stars",
            "purchased": False,
            "selected": False
        },
        {
            "id": 6,
            "name": "Nuage Blanc",
            "price": 140,
            "description": "Un nuage blanc duveteux",
            "image_path": "assets/decorations/cloud_white.png",
            "category": "clouds",
            "purchased": False,
            "selected": False
        },
        {
            "id": 7,
            "name": "Fleur Rose",
            "price": 180,
            "description": "Une fleur rose délicate",
            "image_path": "assets/decorations/flower_pink.png",
            "category": "flowers",
            "purchased": False,
            "selected": False
        },
        {
            "id": 8,
            "name": "Cœur Vert",
            "price": 120,
            "description": "Un cœur vert émeraude",
            "image_path": "assets/decorations/heart_green.png",
            "category": "hearts",
            "purchased": False,
            "selected": False
        }
    ]
    
    # Créer le répertoire data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Sauvegarder les items par défaut
    with open("data/shop_items.json", "w", encoding="utf-8") as file:
        json.dump(default_items, file, ensure_ascii=False, indent=4)
    
    return default_items

def save_items(items):
    """Sauvegarde les items dans un fichier JSON"""
    os.makedirs("data", exist_ok=True)
    with open("data/shop_items.json", "w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=4)

def load_player_data():
    """Charge les données du joueur"""
    if os.path.exists("data/player_data.json"):
        try:
            with open("data/player_data.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except:
            pass
    
    # Données par défaut
    default_data = {"coins": 500, "selected_items": []}
    
    # Créer le répertoire data s'il n'existe pas
    os.makedirs("data", exist_ok=True)
    
    # Sauvegarder les données par défaut
    with open("data/player_data.json", "w", encoding="utf-8") as file:
        json.dump(default_data, file, ensure_ascii=False, indent=4)
    
    return default_data

def save_player_data(player_data):
    """Sauvegarde les données du joueur"""
    os.makedirs("data", exist_ok=True)
    with open("data/player_data.json", "w", encoding="utf-8") as file:
        json.dump(player_data, file, ensure_ascii=False, indent=4)