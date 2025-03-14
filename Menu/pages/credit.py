from shared.common_utils import draw_text, draw_textbox
from shared.common_ui import *


def show_credit(screen, W, H, mouse_pos, mouse_clicked):

    draw_text("Crédits", BUTTON_FONT, BLACK, screen, W // 2, 100)

    draw_text("Développé par: Robin Loisil", SMALL_FONT, BLACK, screen, W // 2, 300)
    draw_text("Musique et sons: Mozart ", SMALL_FONT, BLACK, screen, W // 2, 350)
    draw_text("Merci d'avoir joué à DRAWWY !", SMALL_FONT, BLACK, screen, W // 2, 400)

    # Bouton retour
    back_button_rect = draw_textbox("RETOUR", W // 2 - 100, H - 100, 
                                    200, 50, SMALL_FONT, BLACK, ORANGE, screen, 25)

    if mouse_clicked and back_button_rect.collidepoint(mouse_pos[0], mouse_pos[1]):
        return screen, "home"

    return screen, "credits"