from shared.utils.common_utils import draw_text
from shared.ui.common_ui import *
from shared.ui.elements import Button


def show_credit(screen, W, H, mouse_pos, mouse_clicked, buttons):
    """
    Affiche l'interface des credits (les personnes qui ont aidé a la
    création du jeu)

    Arguments:
        screen {Surface} -- La surface de l'écran
        W {int} -- La largeur de l'écran
        H {int} -- La hauteur de l'écran
        mouse_pos {tuple} -- La position actuelle de la souris
        mouse_clicked {bool} -- Si le bouton gauche de la souris est cliqué
        buttons {dict} -- Les boutons de l'interface

    Returns:
        tuple -- Le tuple contenant la surface de l'écran, le nom de la page
        courante et les boutons de l'interface
    """
    draw_text("Credits", BUTTON_FONT, BLACK, screen, W // 2, 180)

    draw_text(
        "Developpe par:",
        MEDIUM_FONT,
        BLACK,
        screen,
        W // 2,
        400)
    draw_text("- Alexandre Garin: Staff Engineer/Debuger", SMALL_FONT, (255, 102, 102), screen, W // 2, 450, True)
    draw_text("- Robin Loisil: UX/UI Designer/Developer", SMALL_FONT, (255, 204, 102), screen, W // 2, 500, True)
    draw_text("- Maxence Tardivel: Expert Developper", SMALL_FONT, (255, 153, 255), screen, W // 2, 550, True)
    draw_text("- Logo realise par @artlouveuh", SMALL_FONT, (255, 0, 100), screen, W // 2, 600, True)
    draw_text(
        "Merci d'avoir joué à DRAWWY !",
        MEDIUM_FONT,
        ORANGE,
        screen,
        W // 2,
        700)

    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    buttons["back"].draw(screen, mouse_pos)
    if buttons["back"].hover and mouse_clicked:
        return screen, "home", buttons

    return screen, "credits", buttons
