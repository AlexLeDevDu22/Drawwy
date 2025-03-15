from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text
from shared.ui.elements import Button
from shared.tools import generate_particles
import pygame
import math
import random

def show_home(screen, W, H, mouse_pos, mouse_click, title_angle, particles):
   
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
   
    # Chargement et affichage de l'image du titre
    title_img = pygame.image.load("assets/logo.png").convert_alpha()
    
    # Animation de l'image du titre (échelle)
    title_scale = 1.0 + 0.05 * math.sin(title_angle * 2)
    orig_width, orig_height = title_img.get_size()
    scaled_width = int(orig_width * title_scale)
    scaled_height = int(orig_height * title_scale)
    title_img_scaled = pygame.transform.scale(title_img, (scaled_width, scaled_height))
    
    # Position de l'image (centrée)
    title_x = W // 2 - scaled_width // 2
    title_y = main_panel_y + 100
    
    # Ombre du titre (optionnel)
    shadow_img = title_img_scaled.copy()
    shadow_img.fill((100, 100, 100, 150), None, pygame.BLEND_RGBA_MULT)
    screen.blit(shadow_img, (title_x + 8, title_y + 8))
    
    # Affichage du titre
    screen.blit(title_img_scaled, (title_x, title_y))
   
    # Boutons
    for i, button_text in enumerate(["JOUER", "SUCCÈS", "QUITTER"]):
        button=Button("center",
                           int(main_panel_y + 320 + i * 1.3 * 80),
                           w=500,
                           text=button_text)
       
        # Gestion des clics
        if button.check_hover(mouse_pos) and mouse_click:
            if button_text == "QUITTER":
                pygame.quit()
                sys.exit()
            elif button_text == "JOUER":
                return screen, "play", particles
            elif button_text == "SUCCÈS":
                return screen, "achievements", particles
       
        button.draw(screen)
    
    # Shop
    button_radius = 50
    shop_button=Button(main_panel_x + button_radius + 10,
                        main_panel_y + main_panel_height- button_radius*2 - 10,
                        radius=button_radius,
                        circle=True,
                        text_font=VERY_SMALL_FONT,
                        image="assets/icon_shop.png")
                       
    if shop_button.check_hover(mouse_pos) and mouse_click:
        return screen, "shop", particles
    shop_button.draw(screen)
    
    # Crédits
    credit_button=Button(main_panel_x + main_panel_width - button_radius - 10,
                        main_panel_y + main_panel_height- button_radius*2 - 10,
                        text="CRÉDIT",
                        radius=button_radius,
                        circle=True,
                        text_font=VERY_SMALL_FONT)
                       
    if credit_button.check_hover(mouse_pos) and mouse_click:
        return screen, "credits", particles
    credit_button.draw(screen)
    
    # Effets de particules lors du clic
    if mouse_click:
        particles+=generate_particles(20, mouse_pos[0]-30, mouse_pos[1]-30, mouse_pos[0]+30, mouse_pos[1]+30)
    
    return screen, "home", particles