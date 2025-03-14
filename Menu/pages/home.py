from shared.common_ui import *
from shared.common_utils import draw_text
from shared.tools import generate_particles

import pygame
import math
import random

def show_home(screen, W,H,mouse_pos, mouse_click, title_angle, particles):
    
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
    
    # Titre avec effet d'animation
    title_scale = 1.0 + 0.05 * math.sin(title_angle * 2)
    title_size = int(280 * title_scale)
    TITLE_FONT_animated = pygame.font.SysFont(None, title_size)
    
    # Ombre du titre
    draw_text("DRAWWY", TITLE_FONT_animated, GRAY, screen, 
            W // 2 + 8, main_panel_y + 150 + 8)
    
    # Titre
    draw_text("DRAWWY", TITLE_FONT_animated, BLACK, screen, 
            W // 2, main_panel_y + 150)
    
    
    # Boutons
    buttons = ["JOUER", "SUCCÈS", "QUITTER"]
    button_width = 500
    button_height = 80
    button_x = (W - button_width) // 2
    button_y_start = main_panel_y + 320
    buttons_offsets=5
    for i, button_text in enumerate(buttons):
        button_y = int(button_y_start + i * 1.3 * button_height)
        
        # Animation de survol
        hover = button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height
        
        
        # Dessiner l'ombre du bouton
        pygame.draw.rect(screen, DARK_BEIGE if not hover else GRAY, 
                    (button_x + buttons_offsets, button_y + buttons_offsets, button_width, button_height), 
                    border_radius=40)
        
        # Dessiner le bouton
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(screen, 
                        SOFT_ORANGE if hover else ORANGE, 
                        button_rect, 
                        border_radius=40)
        

        # Texte du bouton avec un léger déplacement lorsqu'il est survolé
        text_y_offset = 3 if hover else 0
        draw_text(button_text, BUTTON_FONT, BLACK, screen, 
                button_x + button_width // 2, 
                button_y + button_height // 2 - text_y_offset)
        
        # Gestion des clics
        if mouse_click and hover:
            particles+=generate_particles(20,button_x, button_y, button_x+button_width, button_y+button_height)
            
            if button_text == "QUITTER":
                pygame.quit()
                sys.exit()
            elif button_text == "JOUER":
                return screen, "play", particles
            elif button_text == "SUCCÈS":
                return screen, "achievements", particles

        # Crédits

        # Dessiner le bouton rond "crédit"
        credit_button_radius = 50
        credit_button_x = main_panel_x + main_panel_width - credit_button_radius - 10
        credit_button_y = main_panel_y + main_panel_height- credit_button_radius - 10
        buttons_offsets=4
        
        # Animation de survol du credit
        hover_credit = math.sqrt((mouse_pos[0] - credit_button_x)**2 + (mouse_pos[1] - credit_button_y)**2) <= credit_button_radius
        # Dessiner le cercle
        pygame.draw.circle(screen, 
                        DARK_BEIGE if not hover_credit else GRAY, 
                        (credit_button_x + buttons_offsets-1, credit_button_y + buttons_offsets), 
                        credit_button_radius)
        pygame.draw.circle(screen, 
                        SOFT_ORANGE if hover_credit else ORANGE,
                        (credit_button_x, credit_button_y),
                        credit_button_radius)

        # Texte du bouton CREDit avec un léger déplacement lorsqu'il est survolé
        credit_text_y_offset = 3 if hover_credit else 0
        draw_text("CRÉDIT", VERY_SMALL_FONT, BLACK, screen, 
                credit_button_x, 
                credit_button_y - credit_text_y_offset)
        
        if hover_credit and mouse_click:
            particles+=generate_particles(20,credit_button_x-credit_button_radius, credit_button_y-credit_button_radius, credit_button_x+credit_button_radius, credit_button_y+credit_button_radius)
            return screen, "credits", particles
        

    # Effets de particules lors du clic
    if mouse_click:
        particles+=generate_particles(20, mouse_pos[0]-30, mouse_pos[1]-30, mouse_pos[0]+30, mouse_pos[1]+30)

    return screen, "home", particles