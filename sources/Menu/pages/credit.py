from shared.utils.common_utils import draw_text
from shared.ui.common_ui import *
from shared.ui.elements import Button


def show_credit(screen, W, H, mouse_pos, mouse_clicked, buttons):

    draw_text("Crédits", BUTTON_FONT, BLACK, screen, W // 2, 100)

    draw_text(
        "Fait grace à:",
        MEDIUM_FONT,
        BLACK,
        screen,
        W // 2,
        300)    
    draw_text("- Alexandre Garin: Staff Engineer", SMALL_FONT, (255, 102, 102), screen, W // 2, 350, True)
    draw_text("- Robin Loisil: UX/UI Designer/Developer", SMALL_FONT, (255, 204, 102), screen, W // 2, 400, True)
    draw_text("- Maxence Tardivel: Staff Engineer", SMALL_FONT, (255, 153, 255), screen, W // 2, 450, True)
    draw_text(
        "Merci d'avoir joué à DRAWWY !",
        MEDIUM_FONT,
        ORANGE,
        screen,
        W // 2,
        630)

    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    if buttons["back"].check_hover(mouse_pos) and mouse_clicked:
        return screen, "home", buttons
    buttons["back"].draw(screen)

    return screen, "credits", buttons
