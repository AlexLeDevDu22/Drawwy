from shared.utils.common_utils import draw_text
from shared.ui.common_ui import *
from shared.ui.elements import Button


def show_credit(screen, W, H, mouse_pos, mouse_clicked, buttons):

    draw_text("Crédits", BUTTON_FONT, BLACK, screen, W // 2, 100)

    draw_text("Développé par: Robin Loisil", SMALL_FONT, BLACK, screen, W // 2, 300)
    draw_text("Musique et sons: JUL ", SMALL_FONT, BLACK, screen, W // 2, 350)
    draw_text("Merci d'avoir joué à DRAWWY !", SMALL_FONT, BLACK, screen, W // 2, 400)

    # Bouton retour
    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    if buttons["back"].check_hover(mouse_pos) and mouse_clicked:
        return screen, "home", buttons
    buttons["back"].draw(screen)

    return screen, "credits", buttons