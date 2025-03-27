from shared.ui.common_ui import *
from shared.ui.elements import Button
import pygame
import math


def show_home(
        screen,
        W,
        H,
        mouse_pos,
        mouse_click,
        title_angle,
        buttons,
        title_img,
        shadow_img,
        orig_width,
        orig_height):
    """
    Displays the main home screen interface with animated title and interactive buttons.

    Args:
        screen (Surface): The main display surface.
        W (int): The width of the screen.
        H (int): The height of the screen.
        mouse_pos (tuple): Current position of the mouse cursor.
        mouse_click (bool): Indicates whether the mouse has been clicked.
        title_angle (float): Angle used for animating the title image.
        buttons (dict): A dictionary to manage button instances.
        title_img (Surface): Image representing the title.
        shadow_img (Surface): Shadow image for the title.
        orig_width (int): Original width of the title image.
        orig_height (int): Original height of the title image.

    Returns:
        tuple: The updated screen surface, the current page name, and the buttons dictionary.
    """
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

    # Animation de l'image du titre (échelle)
    title_scale = 1.3 + 0.1 * math.sin(title_angle * 1.8)
    scaled_width = int(280 * orig_width / orig_height * title_scale)
    scaled_height = int(280 * title_scale)

    # Optimisation : utilisation de smoothscale pour une meilleure qualité
    title_img_scaled = pygame.transform.smoothscale(
        title_img, (scaled_width, scaled_height))
    shadow_img_scaled = pygame.transform.smoothscale(
        shadow_img, (scaled_width, scaled_height))

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
            buttons[button_text] = Button(
                "center",
                int(
                    main_panel_y + 380 + i * 1.3 * 80 + (
                        20 if button_text == "QUITTER" else 0)),
                w=300 if button_text == "QUITTER" else 350,
                h=70,
                text=button_text)

        # Gestion des clics
        buttons[button_text].draw(screen, mouse_pos)
        if buttons[button_text].hover and mouse_click:
            if button_text == "QUITTER":
                pygame.quit()
                sys.exit()
            elif button_text == "JOUER":
                return screen, "play", buttons
            elif button_text == "SUCCES":
                return screen, "achievements", buttons

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

    shop_button.draw(screen, mouse_pos)
    if shop_button.hover and mouse_click:
        return screen, "shop", buttons

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
        text_font=pygame.font.Font("assets/text_police/Wowsers.ttf", 17))

    credit_button.draw(screen, mouse_pos)
    if credit_button.hover and mouse_click:
        return screen, "credits", buttons

    return screen, "home", buttons
