import pygame
from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text
from shared.ui.elements import Button
from shared.utils.data_manager import *


def show_achievements(
        screen,
        W,
        H,
        mouse_pos,
        mouse_click,
        buttons,
        scroll_y=0):
    """
    Affiche l'interface des succ s (achievements)
    Arguments:
        screen {Surface} -- La surface de l' cran
        W {int} -- La largeur de l'cran
        H {int} -- La hauteur de l'cran
        mouse_pos {tuple} -- La position actuelle de la souris
        mouse_click {bool} -- Si le bouton gauche de la souris est cliqu
        buttons {dict} -- Les boutons de l'interface
        scroll_y {int} -- La hauteur de d placement du d filement
    Returns:
        tuple -- Le tuple contenant la surface de l'cran, le nom de la page courante et les boutons de l'interface
    """
    # Titre
    draw_text("SUCCES", BUTTON_FONT, BLACK, screen, W // 2, 100)
    achievement_height = 70
    total_height = len(PLAYER_DATA["achievements"]) * \
        (achievement_height + 10) + 60
    # Panneau principal
    main_panel_width = 800
    main_panel_height = 500
    main_panel_x = (W - main_panel_width) // 2
    main_panel_y = 180

    pygame.draw.rect(screen, DARK_BEIGE,
                     (main_panel_x + 10, main_panel_y + 10,
                      main_panel_width, main_panel_height),
                     border_radius=30)

    pygame.draw.rect(screen, BEIGE,
                     (main_panel_x, main_panel_y,
                      main_panel_width, main_panel_height),
                     border_radius=30)

    # Calculer la hauteur totale nécessaire pour tous les achievements
    achievement_height = 70
    total_height = len(PLAYER_DATA["achievements"]) * \
        (achievement_height + 10) + 60

    # Barre de défilement
    scrollbar_width = 20
    scrollbar_height = main_panel_height
    scrollbar_x = main_panel_x + main_panel_width - scrollbar_width
    scrollbar_y = main_panel_y

    # Dessiner la barre de défilement
    pygame.draw.rect(
        screen,
        LIGHT_GRAY,
        (scrollbar_x,
         scrollbar_y,
         scrollbar_width,
         scrollbar_height),
        border_radius=10)

    # Dessiner le curseur de défilement
    cursor_height = 210
    cursor_y = scrollbar_y + (scroll_y / total_height) * scrollbar_height
    pygame.draw.rect(screen, GRAY,
                     (scrollbar_x, cursor_y, scrollbar_width, cursor_height),
                     border_radius=10)

    # Dessiner les achievements visibles
    for i, achievement in enumerate(PLAYER_DATA["achievements"]):
        achievement_y = main_panel_y + 10 + i * \
            (achievement_height + 10) - scroll_y
        if main_panel_y <= achievement_y <= main_panel_y + main_panel_height - 70:
            # Fond
            color = PASTEL_GREEN if achievement["succeed"] else LIGHT_GRAY
            pygame.draw.rect(screen, color,
                             (main_panel_x + 50, achievement_y,
                              main_panel_width - 100, achievement_height),
                             border_radius=15)

            # Texte
            draw_text(achievement["title"], SMALL_FONT, BLACK, screen,
                      main_panel_x + 400, achievement_y + 20)

            description_font = pygame.font.SysFont(None, 30)
            draw_text(
                achievement["explication"],
                description_font,
                GRAY,
                screen,
                main_panel_x + 400,
                achievement_y + 50)

            # Icône
            if achievement["succeed"]:
                pygame.draw.circle(
                    screen,
                    DARK_BLUE,
                    (main_panel_x +
                     100,
                     achievement_y +
                     achievement_height //
                     2),
                    20)
                pygame.draw.line(
                    screen,
                    WHITE,
                    (main_panel_x +
                     90,
                     achievement_y +
                     achievement_height //
                     2),
                    (main_panel_x +
                     100,
                     achievement_y +
                     achievement_height //
                     2 +
                     10),
                    4)
                pygame.draw.line(
                    screen,
                    WHITE,
                    (main_panel_x +
                     100,
                     achievement_y +
                     achievement_height //
                     2 +
                     10),
                    (main_panel_x +
                     115,
                     achievement_y +
                     achievement_height //
                     2 -
                     10),
                    4)
            else:
                pygame.draw.circle(
                    screen,
                    GRAY,
                    (main_panel_x +
                     100,
                     achievement_y +
                     achievement_height //
                     2),
                    20)
                pygame.draw.circle(
                    screen,
                    color,
                    (main_panel_x +
                     100,
                     achievement_y +
                     achievement_height //
                     2),
                    16)

            if achievement["succeed"]:
                color = achievement["couleurs"]
                b_size = 3
            else:
                color = (min(255,
                             achievement["couleurs"][0] + 50),
                         min(255,
                             achievement["couleurs"][1] + 50),
                         min(255,
                             achievement["couleurs"][2] + 50))
                b_size = 2

            pygame.draw.rect(screen,
                             SOFT_ORANGE if achievement["succeed"] else GRAY,
                             (main_panel_x + main_panel_width - 115 - b_size,
                              achievement_y + (achievement_height - 50) // 2 - b_size,
                                 50 + b_size * 2,
                                 50 + b_size * 2),
                             border_radius=12)
            pygame.draw.rect(screen,
                             color,
                             (main_panel_x + main_panel_width - 115,
                              achievement_y + (achievement_height - 50) // 2,
                                 50,
                                 50),
                             border_radius=12)

    # Bouton de retour
    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    buttons["back"].draw(screen, mouse_pos)
    if buttons["back"].hover and mouse_click:
        return screen, "home", buttons

    return screen, "achievements", buttons
