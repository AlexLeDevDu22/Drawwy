from Menu.utils.avatar_manager import AvatarManager
from Menu.ui.elements import *
from Menu.pages import achievements
from Menu.pages import play
from Menu.pages import home
from Menu.pages import credit
from shared.common_utils import *

import Menu.pages.play as play
import shared.tools as tools
import yaml
import pygame
import sys
import random
from datetime import datetime
from shared.common_ui import *
from SoloGame import SoloGame
from MultiGame import MultiGame

if sys.platform.startswith("win"):
    import pygetwindow as gw

with open("assets/config.yaml", "r") as f:
    config = yaml.safe_load(f)

pygame.init()
W, H = tools.get_screen_size()
screen = pygame.display.set_mode((W, H))
pygame.display.set_icon(pygame.image.load("assets/icon.png"))
pygame.display.set_caption("Drawwy")

try:gw.getWindowsWithTitle("Drawwy")[0].activate()  # First plan
except:pass

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
current_page = "home"
# Créer le gestionnaire d'avatar
avatar_manager = AvatarManager(screen)

clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    if datetime.now().second==(last_sec_check_connection+2)%60:
        last_sec_check_connection=datetime.now().second
        connected=tools.is_connected()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (1,3):
            mouse_click = True
            
        # Donner priorité aux événements d'avatar s'il est en cours d'édition
        if avatar_manager.handle_event(event, mouse_pos, pygame.mouse.get_pressed()):
            continue  # Événement déjà traité par le gestionnaire d'avatar
    
    # Mise à jour des éléments d'arrière plan
    for element in drawing_elements:
        element.update()
    
    if mouse_click:
        particles+=tools.generate_particles(20, mouse_pos[0]-30, mouse_pos[1]-30, mouse_pos[0]+30, mouse_pos[1]+30)

    # Mise à jour des particules
    for particle in particles[:]:
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)
    
    # Ajouter de nouvelles particules occasionnellement
    if animation_counter % 5 == 0 and len(particles) < 200:
        particles+=tools.generate_particles(10,0, H+10, W, H+10)
    
    # Mise à jour du gestionnaire d'avatar
    avatar_manager.update(mouse_pos, pygame.mouse.get_pressed())
    
    # Fond
    screen.fill(LIGHT_BLUE)

    # Dégradé de fond
    for y in range(H):
        # Interpolation entre deux couleurs pour créer un dégradé
        color = [
            int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / H))
            for i in range(3)
        ]
        pygame.draw.line(screen, color, (0, y), (W, y))
    
    # Dessiner les éléments de dessin en arrière-plan
    for element in drawing_elements:
        element.draw(screen)
    
    # Dessiner les particules
    for particle in particles:
        particle.draw(screen)

    avatar_manager.draw()
    if not (avatar_manager.show_buttons or avatar_manager.is_expanding or avatar_manager.is_retracting):
        # === ÉCRAN DU MENU PRINCIPAL ===
        if current_page == "home":
            # Mise à jour de l'animation
            animation_counter += 1
            title_angle += 0.02
            screen, current_page, particles = home.show_home(screen, W, H, mouse_pos, mouse_click, title_angle, particles)
        # === CHOIX DU MODE DE JEUX ===
        elif current_page == "play":
            screen, current_page = play.play_choicer(screen, W,H, mouse_pos, mouse_click, connected)
        elif current_page == "SoloGame":
            SoloGame(screen)
            current_page="home"
        elif current_page == "MultiGame":
            MultiGame(screen, clock, W, H)
            current_page="home"
        # === ÉCRAN DES SUCCÈS ===
        elif current_page == "achievements":
            screen, current_page = achievements.show_achievements(screen, W,H, mouse_pos, mouse_click)
        elif current_page == "credits":
            screen, current_page = credit.show_credit(screen, W,H, mouse_pos, mouse_click)
        
    # Afficher la version
    version_text = "DRAWWY v1.0"
    text_surface = VERY_SMALL_FONT.render(version_text, True, BLACK)
    screen.blit(text_surface, (20, H - 30))
    
    pygame.display.flip()
    clock.tick(config["game_page_fps"])

pygame.quit()
sys.exit()