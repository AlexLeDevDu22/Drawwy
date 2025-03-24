from shared.utils.common_utils import draw_text
from shared.ui.common_ui import *
from shared.ui.elements import Button


def show_credit(screen, W, H, mouse_pos, mouse_clicked, buttons):

    draw_text("Credits", BUTTON_FONT, BLACK, screen, W // 2, 180)

    draw_text(
        "Developpe par:",
        MEDIUM_FONT,
        BLACK,
        screen,
        W // 2,
        400)
    draw_text("- Alexandre Garin: Staff Engineer", SMALL_FONT, (255, 102, 102), screen, W // 2, 450, True)
    draw_text("- Robin Loisil: UX/UI Designer/Developer", SMALL_FONT, (255, 204, 102), screen, W // 2, 500, True)
    draw_text("- Maxence Tardivel: Staff Engineer", SMALL_FONT, (255, 153, 255), screen, W // 2, 550, True)
    draw_text(
        "Merci d'avoir joué à DRAWWY !",
        MEDIUM_FONT,
        ORANGE,
        screen,
        W // 2,
        700)

    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    if buttons["back"].check_hover(mouse_pos) and mouse_clicked:
        return screen, "home", buttons
    buttons["back"].draw(screen)

    return screen, "credits", buttons
