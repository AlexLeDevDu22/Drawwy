from Menu.utils.avatar_manager import AvatarManager
from Menu.ui.elements import *
from shared.utils.common_utils import AchievementManager
from Menu.pages import play, home, credit, shop, achievements, choice_server
from shared.utils.common_utils import *
from shared.utils.data_manager import *
import Menu.pages.play as play
import shared.tools as tools
import data.shop_updater as updater

import pygame
import threading
import sys
import random
from datetime import datetime
from shared.ui.common_ui import *
from MultiGame import MultiGame
from SoloGame import soloGame
from shared.ui.common_ui import *
from MultiGame import MultiGame
from SoloGame import soloGame

if sys.platform.startswith("win"):
    import pygetwindow as gw

# check for shop update
threading.Thread(target=updater.check_for_shop_updates).start()

pygame.init()
W, H = tools.get_screen_size()
screen = pygame.display.set_mode((W, H))
pygame.display.set_icon(pygame.image.load("assets/icon.png"))
pygame.display.set_caption("Drawwy")

try:gw.getWindowsWithTitle("Drawwy")[0].activate()  # First plan
except:pass

buttons={}

# Créer quelques éléments de dessin flottants
drawing_elements = [BackgroundElement(random.randint(0, W), random.randint(0, H)) for _ in range(50)]

# Liste pour stocker les particules
particles = []

# Paramètres d'animation
animation_counter = 0
title_angle = 0

connected=tools.is_connected()
last_sec_check_connection=datetime.now().second

# État du jeu
last_current_page = "home"
current_page = "home"

# Créer le gestionnaire d'avatar
avatar_manager = AvatarManager(screen)

if PLAYER_DATA["selected_items"]["Curseurs"]:
    cursor=CustomCursor(SHOP_ITEMS[PLAYER_DATA["selected_items"]["Curseurs"]]["image_path"])
else:
    cursor=CustomCursor(None)

clock = pygame.time.Clock()
running = True

# Initialiser scroll_y et total_height
scroll_y = 0
total_height = 0
achievements_manager=AchievementManager(W,H)

while running:

    #achievement id 14 (leleu)
    nom = PLAYER_DATA["pseudo"].lower
    if nom == ("leleu" or nom == "mr leuleu" or nom== "fred leleu" or nom == "frederic leleu"):
        achievements_manager.new_achievement(14)


    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    if datetime.now().second == (last_sec_check_connection + 2) % 60:
        last_sec_check_connection = datetime.now().second
        connected = tools.is_connected()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
            mouse_click = True
        elif event.type == pygame.MOUSEWHEEL:  # Utilisez MOUSEWHEEL pour la molette
            if event.y > 0:  # Molette vers le haut
                scroll_y = max(0, scroll_y - 30)
            elif event.y < 0:  # Molette vers le bas
                scroll_y = min(700, scroll_y + 30)

        avatar_manager.handle_event(event, mouse_pos, achievements_manager)

    # Mise à jour des particules
    if mouse_click:
        particles += tools.generate_particles(20, mouse_pos[0] - 30, mouse_pos[1] - 30, mouse_pos[0] + 30, mouse_pos[1] + 30)

    for particle in particles[:]:
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)

    # Ajouter de nouvelles particules occasionnellement
    if animation_counter % 5 == 0 and len(particles) < 200:
        particles += tools.generate_particles(10, 0, H + 10, W, H + 10)

    # Mise à jour du gestionnaire d'avatar
    avatar_manager.update(mouse_pos, pygame.mouse.get_pressed())

    # Fond
    screen.fill(LIGHT_BLUE)

    # Dégradé de fond
    for y in range(H):
        color = [
            int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / H))
            for i in range(3)
        ]
        pygame.draw.line(screen, color, (0, y), (W, y))

    # Dessiner les éléments de dessin en arrière-plan
    for element in drawing_elements:
        element.update()
        element.draw(screen)

    # Dessiner les particules
    for particle in particles:
        particle.draw(screen)

    if last_current_page != current_page:
        buttons = {}
        pygame.display.set_caption(f"Drawwy - {current_page}")
        last_current_page = current_page

    avatar_manager.draw()

    if not (avatar_manager.show_buttons or avatar_manager.is_expanding or avatar_manager.is_retracting):
        # === ÉCRAN DU MENU PRINCIPAL ===
        if current_page == "home":
            animation_counter += 1
            title_angle += 0.02
            screen, current_page, buttons = home.show_home(screen, W, H, mouse_pos, mouse_click, title_angle, buttons)
        # === CHOIX DU MODE DE JEUX ===
        elif current_page == "play":
            screen, current_page, buttons = play.play_choicer(screen, W, H, mouse_pos, mouse_click, connected, buttons)
        elif current_page == "Solo":
            soloGame(screen, cursor, achievements_manager)
            current_page = "home"
        elif current_page=="Select server":
            screen, current_page, buttons, server_name = choice_server.choice_server(screen, W, H, mouse_pos, mouse_click, connected, buttons)
        elif current_page == "Multi":
            MultiGame(screen, cursor, clock, W, H, achievements_manager, server_name)
            current_page = "home"
        # === ÉCRAN DES SUCCÈS ===
        elif current_page == "achievements":
            screen, current_page, buttons= achievements.show_achievements(screen, W, H, mouse_pos, mouse_click, buttons, scroll_y)
        # === ÉCRAN DES Crédits ===
        elif current_page == "credits":
            screen, current_page, buttons = credit.show_credit(screen, W, H, mouse_pos, mouse_click, buttons)
        # === ÉCRAN DU SHOP ===
        elif current_page == "shop":
            screen, cursor, current_page, buttons, achievements_manager = shop.show_shop(screen, cursor, W, H, mouse_pos, mouse_click, buttons, achievements_manager)

    # Afficher la version
    draw_text("DRAWWY v1.0", VERY_SMALL_FONT, BLACK, screen, 20, H - 30)

    achievements_manager.draw_popup_if_active(screen)

    cursor.show(screen, mouse_pos, True in pygame.mouse.get_pressed())
    
    pygame.display.flip()
    clock.tick(CONFIG["fps"])

pygame.quit()
sys.exit()