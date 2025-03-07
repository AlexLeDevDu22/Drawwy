import pygame
import sys

pygame.init()

info_ecran = pygame.display.Info()
largeur, hauteur = info_ecran.current_w, info_ecran.current_h

ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("DRAWWY")

white = (255, 255, 255)
black = (0, 0, 0)
gray = (170, 170, 170)
light_gray = (200, 200, 200)  # Couleur plus claire pour le survol

font = pygame.font.SysFont(None, 300)
small_font = pygame.font.SysFont(None, 80)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ecran.fill(white)

    draw_text("DRAWWY", font, black, ecran, largeur // 2, 200)

    buttons = ["JOUER", "SUCCÈS", "PARAMÈTRES", "QUITTER"]
    button_y_start = 400
    button_height = 100
    button_width = 500
    button_x = (largeur - button_width) // 2

    for i, button_text in enumerate(buttons):
        button_y = button_y_start + i * 1.4 * button_height
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Changer la couleur si la souris est sur le bouton
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(ecran, light_gray, button_rect, border_radius=100)
        else:
            pygame.draw.rect(ecran, gray, button_rect, border_radius=100)

        draw_text(button_text, small_font, black, ecran, button_x + button_width // 2, button_y + button_height // 2)

    pygame.display.flip()

pygame.quit()
sys.exit()
