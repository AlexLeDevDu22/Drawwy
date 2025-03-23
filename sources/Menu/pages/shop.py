from shared.ui.common_ui import *
from shared.utils.common_utils import CustomCursor
from shared.utils.common_utils import draw_text
from shared.utils.data_manager import *
import shared.tools as tools
import pygame
import random


state = {
            "current_page": 0,
            "selected_category": "Tous",
            "selection_mode": False
        }
def show_shop(
        screen,
        cursor,
        W,
        H,
        mouse_pos,
        mouse_click,
        buttons,
        achievement_manager):
    """Affiche l'interface de la boutique des objets de décoration"""
    # Panneau principal (effet papier)
    main_panel_width = 1100
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
    
    # Etoiles
    num_stars = 0
    for theme in SOLO_THEMES:
        for image in theme["images"]:
            num_stars += image["stars"]

    star_icon = pygame.image.load("assets/icon_star.png")
    star_icon = pygame.transform.scale(star_icon, (40, 40))
    star_icon_rect = star_icon.get_rect(
        center=(
            main_panel_x +
            115,
            main_panel_y +
            76))
    screen.blit(star_icon, star_icon_rect)

    draw_text("X"+str(num_stars), MEDIUM_FONT, BLACK, screen,
              main_panel_x + 142 + MEDIUM_FONT.size("X"+str(num_stars))[0] // 2, main_panel_y + 78)

    # Titre
    draw_text("BOUTIQUE", BUTTON_FONT, GRAY, screen,
              W // 2 + 2, main_panel_y + 80 + 2)
    draw_text("BOUTIQUE", BUTTON_FONT, BLACK, screen,
              W // 2, main_panel_y + 80)

    # Afficher le solde
    draw_text(str(PLAYER_DATA["coins"]), MEDIUM_FONT, BLACK, screen,
              main_panel_x + main_panel_width - 100, main_panel_y + 78)

    coin_icon = pygame.image.load("assets/icon_coin.png")
    coin_icon = pygame.transform.scale(coin_icon, (40, 40))
    coin_icon_rect = coin_icon.get_rect(
        center=(
            main_panel_x +
            main_panel_width -
            MEDIUM_FONT.size(
                str(PLAYER_DATA["coins"]))[0] //
            2 -
            126,
            main_panel_y +
            76))
    screen.blit(coin_icon, coin_icon_rect)

    SHOP_ITEMS_per_page = 4
    categories = ["Tous"] + list(set(item["category"] for item in SHOP_ITEMS))

    # Dessiner les onglets de catégories
    tab_width = 165
    tab_height = 50
    tab_margin = 10
    start_x = main_panel_x + \
        (main_panel_width - (len(categories) * (tab_width + tab_margin) - tab_margin)) // 2

    for i, category in enumerate(categories):
        tab_x = start_x + i * (tab_width + tab_margin)
        tab_y = main_panel_y + 140

        # Animation de survol
        hover = tab_x <= mouse_pos[0] <= tab_x + \
            tab_width and tab_y <= mouse_pos[1] <= tab_y + tab_height

        # Couleur de fond basée sur sélection/survol
        if category == state["selected_category"]:
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
            state["selected_category"] = category
            state["current_page"] = 0

    # Filtrer les SHOP_ITEMS selon la catégorie sélectionnée
    filtered_SHOP_ITEMS = [item for item in SHOP_ITEMS if state["selected_category"]
                           == "Tous" or item["category"] == state["selected_category"]]

    # Calculer le nombre total de pages
    total_pages = max(1, (len(filtered_SHOP_ITEMS) - 1) //
                      SHOP_ITEMS_per_page + 1)

    # Limiter la page courante
    state["current_page"] = min(
        state["current_page"], total_pages - 1)

    # Afficher les SHOP_ITEMS
    start_idx = state["current_page"] * SHOP_ITEMS_per_page
    item_width = 0.42 * main_panel_width
    item_height = 180
    item_margin = 30

    for i in range(min(SHOP_ITEMS_per_page,
                       len(filtered_SHOP_ITEMS) - start_idx)):
        item = filtered_SHOP_ITEMS[start_idx + i]
        item_x = (W-item_margin)//2 - item_width + (i % 2) * (item_width + item_margin)
        item_y = main_panel_y + 220 + (i // 2) * (item_height + item_margin)

        # Animation de survol
        hover_item = item_x <= mouse_pos[0] <= item_x + \
            item_width and item_y <= mouse_pos[1] <= item_y + item_height

        is_selected = item["category"] == "Emotes" or item["index"] == PLAYER_DATA["selected_items"][item["category"]]
        # Couleur de fond basée sur sélection/achat/survol
        if item["index"] in PLAYER_DATA["purchased_items"] and is_selected:
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
        if item["category"] == "Emotes":
            tools.show_emote(screen,
                            PYGAME_EMOTES[item["index"]],
                            item_x + 20,  # Déplacer l'image vers la gauche
                            item_y + item_height // 2 - 50,
                            100)
        else:
            item_img = pygame.image.load(item["image_path"])
            item_img = pygame.transform.scale(item_img, (100, 100))

            img_rect = item_img.get_rect(
                center=(item_x + 70, item_y + item_height // 2))
            screen.blit(item_img, img_rect)

        # Nom de l'item
        draw_text(item["name"], SMALL_FONT, BLACK, screen,
                item_x + 225, item_y + 40)  # Déplacer le texte plus à droite

        # Description de l'item
        draw_text(item["description"], VERY_SMALL_FONT, GRAY, screen,
                  item_x + 300, item_y + 76)

        # Ajout de la rareté
        if "rarity" in item:
            # Définir la couleur selon la rareté
            rarity_colors = {
                "Commun": (30, 180, 60),      # Gris foncé, neutre et terne  
                "Rare": (30, 80, 255),          # Bleu profond, plus distinct  
                "Epique": (160, 40, 220),         # Violet intense  
                "Legendaire": (255, 140, 0)      # Or vif, plus saturé  
            }

            rarity_color = rarity_colors.get(item["rarity"], (100, 100, 100))

            # Afficher la rareté sous la description
            draw_text(item["rarity"], VERY_SMALL_FONT, rarity_color, screen,
                      item_x + 225, item_y + 115)

        # Prix ou statut
        if item["index"] in PLAYER_DATA["purchased_items"]:
            status_text = "ACHETÉ"
            if is_selected and item["category"] != "Emotes":
                status_text = "SÉLECTIONNÉ"
            else:
                status_text = "DEBLOQUÉ"
            status_color = (50, 150, 50) if is_selected else (100, 100, 100)
            draw_text(status_text, SMALL_FONT, status_color, screen,
                      item_x + 220, item_y + 150)
        else:
            if item["category"] != "Bordures":
                price_color = (
                    0,
                    100,
                    0) if PLAYER_DATA["coins"] >= int(
                    item["price"]) else (
                    150,
                    0,
                    0)
                draw_text(str(item['price']), SMALL_FONT, price_color, screen,
                        item_x + 220, item_y + 150)
                coin_icon_rect = coin_icon.get_rect(
                    center=(item_x + 245 + SMALL_FONT.size(str(item['price']))[0]//2, item_y + 150))
                screen.blit(coin_icon, coin_icon_rect)
            else:
                draw_text(str(item['stars_needed']), SMALL_FONT, (0, 0, 150), screen,
                        item_x + 220, item_y + 150)
                coin_icon_rect = star_icon.get_rect(
                    center=(item_x + 245 + SMALL_FONT.size(str(item['stars_needed']))[0]//2, item_y + 150))
                screen.blit(star_icon, coin_icon_rect)

        achievement_manager.draw_popup_if_active(screen)

        # Gestion des clics sur les SHOP_ITEMS
        if mouse_click and hover_item:
            if item["index"] in PLAYER_DATA["purchased_items"]:
                cursor_ = toggle_select(item, cursor)
                if cursor_:
                    cursor = cursor_

            elif item["category"] != "Bordures" and PLAYER_DATA["coins"] >= item["price"]:
                PLAYER_DATA["coins"] -= item["price"]
                PLAYER_DATA["purchased_items"].append(item["index"])
                PLAYER_DATA["coins"] = PLAYER_DATA["coins"]

                # ALL ACHIEVEMENT EN RAPPORT AVEC LES ITEMS
                list_cursers = [e["index"] in PLAYER_DATA["purchased_items"]
                                for e in SHOP_ITEMS if e["category"] == "Curseurs"]
                list_borders = [e["index"] in PLAYER_DATA["purchased_items"]
                                for e in SHOP_ITEMS if e["category"] == "Bordures"]
                list_emotes = [e["index"] in PLAYER_DATA["purchased_items"]
                               for e in SHOP_ITEMS if e["category"] == "Emotes"]
                list_all = [e["index"] in PLAYER_DATA["purchased_items"]
                            for e in SHOP_ITEMS]
                if item["category"] == "Curseurs":
                    achievement_manager.new_achievement(5)

                if all(list_cursers):
                    achievement_manager.new_achievement(6)

                if item["category"] == "Bordures":
                    achievement_manager.new_achievement(7)

                if all(list_borders):
                    achievement_manager.new_achievement(8)

                if item["category"] == "Emotes":
                    achievement_manager.new_achievement(9)

                if all(list_emotes):
                    achievement_manager.new_achievement(10)

                if all(list_all):
                    achievement_manager.new_achievement(11)

                save_data("PLAYER_DATA")

    # Boutons de pagination
    if total_pages > 1:
        nav_width = 60
        nav_height = 60
        prev_x = main_panel_x + main_panel_width // 2 - nav_width - 20
        next_x = main_panel_x + main_panel_width // 2 + 20
        nav_y = main_panel_y + main_panel_height - 100

        # Bouton précédent
        prev_hover = prev_x <= mouse_pos[0] <= prev_x + \
            nav_width and nav_y <= mouse_pos[1] <= nav_y + nav_height
        prev_color = SOFT_ORANGE if prev_hover else ORANGE

        if state["current_page"] > 0:
            # Ombre
            pygame.draw.circle(
                screen,
                DARK_BEIGE,
                (prev_x + nav_width // 2 + 4,
                 nav_y + nav_height // 2 + 4),
                nav_width // 2)
            # Cercle
            pygame.draw.circle(
                screen,
                prev_color,
                (prev_x + nav_width // 2,
                 nav_y + nav_height // 2),
                nav_width // 2)

            # Flèche
            fleche_gauche = pygame.image.load("assets/fleche_gauche.png")
            fleche_gauche = pygame.transform.scale(fleche_gauche, (40, 40))
            fleche_gauche_rect = fleche_gauche.get_rect(
                center=(prev_x + nav_width // 2, nav_y + nav_height // 2))
            screen.blit(fleche_gauche, fleche_gauche_rect)

            if mouse_click and prev_hover:
                state["current_page"] -= 1

        # Bouton suivant
        next_hover = next_x <= mouse_pos[0] <= next_x + \
            nav_width and nav_y <= mouse_pos[1] <= nav_y + nav_height
        next_color = SOFT_ORANGE if next_hover else ORANGE

        if state["current_page"] < total_pages - 1:
            # Ombre
            pygame.draw.circle(
                screen,
                DARK_BEIGE,
                (next_x + nav_width // 2 + 4,
                 nav_y + nav_height // 2 + 4),
                nav_width // 2)
            # Cercle
            pygame.draw.circle(
                screen,
                next_color,
                (next_x + nav_width // 2,
                 nav_y + nav_height // 2),
                nav_width // 2)
            # Flèche
            fleche_droite = pygame.image.load("assets/fleche_droite.png")
            fleche_droite = pygame.transform.scale(fleche_droite, (40, 40))
            fleche_droite_rect = fleche_droite.get_rect(
                center=(next_x + nav_width // 2, nav_y + nav_height // 2))
            screen.blit(fleche_droite, fleche_droite_rect)

            if mouse_click and next_hover:
                state["current_page"] += 1

        # Afficher numéro de page
        draw_text(
            f"Page {
                state['current_page'] + 1}/{total_pages}",
            SMALL_FONT,
            BLACK,
            screen,
            main_panel_x + main_panel_width // 2,
            nav_y + nav_height + 10)

    # Bouton retour
    back_width = 180
    back_height = 60
    back_x = main_panel_x + main_panel_width - 200
    back_y = main_panel_y + main_panel_height - 100

    # Animation de survol
    hover_back = back_x <= mouse_pos[0] <= back_x + \
        back_width and back_y <= mouse_pos[1] <= back_y + back_height

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
        return screen, cursor, "home", buttons, achievement_manager

    return screen, cursor, "shop", buttons, achievement_manager


def toggle_select(item, cursor):
    # Basculer la sélection
    if item["category"] != "Emotes" and item["index"] == PLAYER_DATA["selected_items"][item["category"]]:  # désélectionner
        if item["category"] == "Curseurs":
            PLAYER_DATA["selected_items"]["Curseurs"] = None
            cursor = CustomCursor(None)
    else:  # sélectionner
        PLAYER_DATA["selected_items"][item["category"]] = item["index"]
        if item["category"] == "Curseurs":
            cursor = CustomCursor(item["image_path"])

    save_data("PLAYER_DATA")
    return cursor
