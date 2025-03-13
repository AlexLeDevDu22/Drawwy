from shared.common_utils import draw_text, draw_textbox


def draw_credits_screen(ecran, largeur, hauteur, button_font, small_font, black, orange, mouse_clicked, mouse_pos):

    draw_text("Crédits", button_font, black, ecran, largeur // 2, 100)

    draw_text("Développé par: [Ton Nom]", small_font, black, ecran, largeur // 2, 300)
    draw_text("Musique et sons: [Nom du compositeur]", small_font, black, ecran, largeur // 2, 350)
    draw_text("Merci d'avoir joué à DRAWWY !", small_font, black, ecran, largeur // 2, 400)

    # Bouton retour
    back_button_rect = draw_textbox("RETOUR", largeur // 2 - 100, hauteur - 100, 
                                    200, 50, small_font, black, orange, ecran, 25)

    if mouse_clicked and back_button_rect.collidepoint(mouse_pos):
        return "menu"

    return "credits"