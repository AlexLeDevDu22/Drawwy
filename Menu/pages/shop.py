import pygame
import json
import os

# Couleurs
BLUE_BG = (135, 206, 250)
BEIGE_PANEL = (255, 230, 180)
ORANGE_BUTTON = (255, 120, 50)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Item:
    def __init__(self, id, name, price, description, image_path, category):
        self.id = id
        self.name = name
        self.price = price
        self.description = description
        self.image_path = image_path
        self.category = category
        self.purchased = False
        self.selected = False
        self.image = None

def load_items():
    """Charge les objets de décoration depuis un fichier JSON ou crée des objets par défaut"""
    if os.path.exists("shop_items.json"):
        try:
            with open("shop_items.json", "r", encoding="utf-8") as file:
                items_data = json.load(file)
                items = []
                for item_data in items_data:
                    item = Item(
                        item_data["id"],
                        item_data["name"],
                        item_data["price"],
                        item_data["description"],
                        item_data["image_path"],
                        item_data["category"]
                    )
                    item.purchased = item_data.get("purchased", False)
                    items.append(item)
                return items
        except Exception as e:
            print(f"Erreur lors du chargement des items: {e}")
    
    # Items par défaut si le fichier n'existe pas
    return [
        Item(1, "Étoile Rose", 100, "Une jolie étoile rose pour décorer", "assets/star_pink.png", "stars"),
        Item(2, "Nuage Bleu", 150, "Un nuage bleu ciel", "assets/cloud_blue.png", "clouds"),
        Item(3, "Fleur Jaune", 200, "Une fleur jaune lumineuse", "assets/flower_yellow.png", "flowers"),
        Item(4, "Cœur Rouge", 120, "Un cœur rouge brillant", "assets/heart_red.png", "hearts"),
        Item(5, "Étoile Verte", 100, "Une étoile verte scintillante", "assets/star_green.png", "stars"),
        Item(6, "Nuage Blanc", 140, "Un nuage blanc duveteux", "assets/cloud_white.png", "clouds"),
        Item(7, "Fleur Rose", 180, "Une fleur rose délicate", "assets/flower_pink.png", "flowers"),
        Item(8, "Cœur Vert", 120, "Un cœur vert émeraude", "assets/heart_green.png", "hearts")
    ]

def save_items(items):
    """Sauvegarde les items dans un fichier JSON"""
    items_data = []
    for item in items:
        items_data.append({
            "id": item.id,
            "name": item.name,
            "price": item.price,
            "description": item.description,
            "image_path": item.image_path,
            "category": item.category,
            "purchased": item.purchased
        })
    
    with open("shop_items.json", "w", encoding="utf-8") as file:
        json.dump(items_data, file, ensure_ascii=False, indent=4)

def load_player_data():
    """Charge les données du joueur"""
    if os.path.exists("player_data.json"):
        try:
            with open("player_data.json", "r") as file:
                return json.load(file)
        except:
            pass
    
    # Données par défaut
    return {"coins": 500, "selected_items": []}

def save_player_data(player_data):
    """Sauvegarde les données du joueur"""
    with open("player_data.json", "w") as file:
        json.dump(player_data, file, indent=4)

def load_images(items):
    """Charge les images des items"""
    for item in items:
        try:
            item.image = pygame.image.load(item.image_path)
            item.image = pygame.transform.scale(item.image, (80, 80))
        except:
            # Image de remplacement si l'image n'est pas trouvée
            item.image = pygame.Surface((80, 80))
            item.image.fill((200, 200, 200))

def draw_rounded_rect(surface, color, rect, radius):
    """Dessine un rectangle avec coins arrondis"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_text(surface, text, size, x, y, color=BLACK, center=True):
    """Dessine du texte à l'écran"""
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
    else:
        text_rect = text_surface.get_rect(topleft=(x, y))
    surface.blit(text_surface, text_rect)
    return text_rect

def show_shop():
    """Affiche l'interface de la boutique"""
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("DRAWWY - Boutique")
    
    # Charger les données
    items = load_items()
    load_images(items)
    player_data = load_player_data()
    coins = player_data.get("coins", 0)
    
    # Variables pour la pagination et filtrage
    items_per_page = 4
    current_page = 0
    selected_category = "tous"
    categories = ["tous"] + list(set(item.category for item in items))
    
    # Position et taille des éléments
    shop_panel = pygame.Rect(100, 80, 600, 440)
    
    # Variable pour le mode "sélection" ou "achat"
    selection_mode = False
    
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Vérifier si un bouton de catégorie est cliqué
                x_start = 150
                for i, category in enumerate(categories):
                    cat_rect = pygame.Rect(x_start + i*100, 90, 80, 30)
                    if cat_rect.collidepoint(mouse_pos):
                        selected_category = category
                        current_page = 0
                
                # Vérifier si un bouton de pagination est cliqué
                if pygame.Rect(350, 480, 50, 30).collidepoint(mouse_pos):  # Bouton précédent
                    if current_page > 0:
                        current_page -= 1
                
                if pygame.Rect(410, 480, 50, 30).collidepoint(mouse_pos):  # Bouton suivant
                    filtered_items = [item for item in items if selected_category == "tous" or item.category == selected_category]
                    if current_page < (len(filtered_items) - 1) // items_per_page:
                        current_page += 1
                
                # Vérifier si le bouton mode est cliqué
                if pygame.Rect(600, 90, 80, 30).collidepoint(mouse_pos):
                    selection_mode = not selection_mode
                
                # Vérifier si un item est cliqué
                filtered_items = [item for item in items if selected_category == "tous" or item.category == selected_category]
                start_idx = current_page * items_per_page
                for i in range(min(items_per_page, len(filtered_items) - start_idx)):
                    item = filtered_items[start_idx + i]
                    item_x = 150 + (i % 2) * 300
                    item_y = 150 + (i // 2) * 150
                    item_rect = pygame.Rect(item_x, item_y, 250, 120)
                    
                    if item_rect.collidepoint(mouse_pos):
                        if selection_mode:
                            if item.purchased:
                                # Basculer la sélection
                                item.selected = not item.selected
                                if item.selected:
                                    if item.id not in player_data.get("selected_items", []):
                                        player_data.setdefault("selected_items", []).append(item.id)
                                else:
                                    if item.id in player_data.get("selected_items", []):
                                        player_data["selected_items"].remove(item.id)
                                save_player_data(player_data)
                        else:
                            # Mode achat
                            if not item.purchased and coins >= item.price:
                                coins -= item.price
                                item.purchased = True
                                player_data["coins"] = coins
                                save_items(items)
                                save_player_data(player_data)
                
                # Vérifier si le bouton retour est cliqué
                if pygame.Rect(100, 520, 100, 40).collidepoint(mouse_pos):
                    running = False
        
        # Dessiner l'écran
        screen.fill(BLUE_BG)
        
        # Dessiner le panneau principal
        draw_rounded_rect(screen, BEIGE_PANEL, shop_panel, 20)
        
        # Dessiner le titre
        draw_text(screen, "BOUTIQUE", 36, screen_width // 2, 50)
        
        # Afficher le solde
        draw_text(screen, f"Pièces: {coins}", 24, 700, 50)
        
        # Dessiner les onglets de catégories
        x_start = 150
        for i, category in enumerate(categories):
            cat_color = ORANGE_BUTTON if category == selected_category else (200, 150, 100)
            cat_rect = pygame.Rect(x_start + i*100, 90, 80, 30)
            draw_rounded_rect(screen, cat_color, cat_rect, 10)
            draw_text(screen, category.capitalize(), 16, x_start + i*100 + 40, 105)
        
        # Bouton mode (sélection/achat)
        mode_rect = pygame.Rect(600, 90, 80, 30)
        mode_color = (100, 200, 100) if selection_mode else (200, 100, 100)
        draw_rounded_rect(screen, mode_color, mode_rect, 10)
        mode_text = "Sélection" if selection_mode else "Achat"
        draw_text(screen, mode_text, 16, 640, 105)
        
        # Filtrer les items selon la catégorie sélectionnée
        filtered_items = [item for item in items if selected_category == "tous" or item.category == selected_category]
        
        # Afficher les items
        start_idx = current_page * items_per_page
        for i in range(min(items_per_page, len(filtered_items) - start_idx)):
            item = filtered_items[start_idx + i]
            item_x = 150 + (i % 2) * 300
            item_y = 150 + (i // 2) * 150
            
            # Fond de l'item
            item_color = (220, 250, 220) if item.selected else BEIGE_PANEL
            item_rect = pygame.Rect(item_x, item_y, 250, 120)
            draw_rounded_rect(screen, item_color, item_rect, 10)
            
            # Image de l'item
            screen.blit(item.image, (item_x + 10, item_y + 20))
            
            # Infos de l'item
            draw_text(screen, item.name, 20, item_x + 140, item_y + 30, center=True)
            draw_text(screen, item.description, 14, item_x + 140, item_y + 60, center=True)
            
            # Prix ou statut
            if item.purchased:
                status_text = "Sélectionné" if item.selected else "Acheté"
                status_color = (50, 150, 50) if item.selected else (100, 100, 100)
                draw_text(screen, status_text, 16, item_x + 140, item_y + 90, color=status_color, center=True)
            else:
                price_color = (0, 100, 0) if coins >= item.price else (150, 0, 0)
                draw_text(screen, f"{item.price} pièces", 16, item_x + 140, item_y + 90, color=price_color, center=True)
        
        # Boutons de pagination
        draw_rounded_rect(screen, ORANGE_BUTTON, pygame.Rect(350, 480, 50, 30), 10)
        draw_rounded_rect(screen, ORANGE_BUTTON, pygame.Rect(410, 480, 50, 30), 10)
        draw_text(screen, "←", 20, 375, 495)
        draw_text(screen, "→", 20, 435, 495)
        draw_text(screen, f"Page {current_page+1}/{max(1, (len(filtered_items)-1)//items_per_page+1)}", 16, 400, 520)
        
        # Bouton retour
        return_button = pygame.Rect(100, 520, 100, 40)
        draw_rounded_rect(screen, ORANGE_BUTTON, return_button, 15)
        draw_text(screen, "RETOUR", 20, 150, 540)
        
        pygame.display.flip()
    
    pygame.quit()
    return

# Pour tester la fonction
if __name__ == "__main__":
    show_shop()