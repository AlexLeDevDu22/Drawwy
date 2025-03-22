from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text
from shared.ui.elements import Button
from shared.tools import generate_particles
import pygame
import math
import random


def show_home(screen, W, H, mouse_pos, mouse_click, title_angle, buttons, title_img, shadow_img, orig_width, orig_height, paper_texture):
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

    # Affichage de la texture papier (optimisation : pré-générée)
    screen.blit(paper_texture, (main_panel_x, main_panel_y))

    # Animation de l'image du titre (échelle)
    title_scale = 1.3 + 0.1 * math.sin(title_angle * 1.8)
    scaled_width = int(280 * orig_width / orig_height * title_scale)
    scaled_height = int(280 * title_scale)

    # Optimisation : utilisation de smoothscale pour une meilleure qualité
    title_img_scaled = pygame.transform.smoothscale(title_img, (scaled_width, scaled_height))
    shadow_img_scaled = pygame.transform.smoothscale(shadow_img, (scaled_width, scaled_height))

    # Position de l'image (centrée)
    title_x = W // 2 - scaled_width // 2
    title_y = main_panel_y 

    # Ombre du titre (optionnel)
    screen.blit(shadow_img_scaled, (title_x + 6, title_y + 6))

    # Affichage du titre
    screen.blit(title_img_scaled, (title_x, title_y))

    # Boutons
    for i, button_text in enumerate(["JOUER", "SUCCES", "QUITTER"]):
        if button_text not in buttons.keys():
            if button_text == "QUITTER":
                buttons[button_text] = Button("center",
                                              int(main_panel_y + 350 + i * 1.3 * 80),
                                              w=300,
                                              h=70,
                                              text=button_text)
            else:
                buttons[button_text] = Button("center",
                                              int(main_panel_y + 350 + i * 1.3 * 80),
                                              w=350,
                                              h=80,
                                              text=button_text)

        # Gestion des clics
        if buttons[button_text].check_hover(mouse_pos) and mouse_click:
            if button_text == "QUITTER":
                pygame.quit()
                sys.exit()
            elif button_text == "JOUER":
                return screen, "play", buttons
            elif button_text == "SUCCES":
                return screen, "achievements", buttons

        buttons[button_text].draw(screen)

    # Shop
    button_radius = 55
    shop_button = Button(
        main_panel_x +
        10,
        main_panel_y +
        main_panel_height -
        button_radius *
        2 -
        10,
        radius=button_radius,
        circle=True,
        text_font=VERY_SMALL_FONT,
        image="assets/icon_shop.png")

    if shop_button.check_hover(mouse_pos) and mouse_click:
        return screen, "shop", buttons
    shop_button.draw(screen)

    # Crédits
    credit_button = Button(
        main_panel_x +
        main_panel_width -
        button_radius *
        2 -
        10,
        main_panel_y +
        main_panel_height -
        button_radius *
        2 -
        10,
        text="CREDIT",
        radius=button_radius,
        circle=True,
        text_font=pygame.font.Font("assets\\text_police\\Wowsers.ttf", 17))

    if credit_button.check_hover(mouse_pos) and mouse_click:
        return screen, "credits", buttons
    credit_button.draw(screen)

    return screen, "home", buttons
