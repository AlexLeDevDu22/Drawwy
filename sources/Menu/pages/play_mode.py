from shared.ui.common_ui import *
from shared.utils.common_utils import *
from shared.ui.elements import Button


def play_choicer(screen, W, H, mouse_pos, mouse_click, connected, buttons):
    """
    Displays the game mode selection screen and handles user interaction.

    Args:
        W (int): The width of the screen.
        H (int): The height of the screen.
        mouse_pos (tuple): The current position of the mouse.
        mouse_click (bool): True if the left mouse button was clicked.
        connected (bool): True if the player is connected to the internet.
        buttons (dict): A dictionary of button elements.

    Returns:
        tuple: A tuple containing:

            - The name of the next page to display.
            - The updated dictionary of buttons.
    """

    game_modes = ["Solo", "Multijoueurs"]
    mode_width = 300
    mode_height = 200
    modes_y = H // 2 - mode_height // 2

    total_width = len(game_modes) * mode_width + (len(game_modes) - 1) * 50
    start_x = (W - total_width) // 2

    for i, mode in enumerate(game_modes):
        mode_x = start_x + i * (mode_width + 50)
        mode_rect = pygame.Rect(mode_x, modes_y, mode_width, mode_height)

        # Vérifier si la souris survole
        hover = mode_rect.collidepoint(mouse_pos) and (
            mode == "Solo" or connected)

        # Dessiner l'ombre
        pygame.draw.rect(screen, DARK_BEIGE,
                         (mode_x + 10, modes_y + 10, mode_width, mode_height),
                         border_radius=20)

        # Dessiner le fond
        color = SOFT_ORANGE if hover else BEIGE
        pygame.draw.rect(screen, color, mode_rect, border_radius=20)

        # Dessiner le texte
        draw_text(
            mode,
            SMALL_FONT,
            BLACK if mode == "Solo" or connected else RED,
            screen,
            mode_x +
            mode_width //
            2,
            modes_y +
            mode_height //
            2)

        # Gérer le clic
        if mouse_click and hover:
            if mode == "Solo" or connected:
                return screen, "Solo" if mode == "Solo" else "Select server", buttons

    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    buttons["back"].draw(screen, mouse_pos)
    if buttons["back"].hover and mouse_click:
        return screen, "home", buttons
    return screen, "play", buttons
