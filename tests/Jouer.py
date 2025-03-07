import pygame
import sys


pygame.init()

info_ecran = pygame.display.Info()
largeur, hauteur = info_ecran.current_w, info_ecran.current_h
# Dimensions de la fenêtre
    
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("DRAWWY")




white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)


font = pygame.font.SysFont(None, 300)
small_font = pygame.font.SysFont(None, 80)

# Fonction pour dessiner le texte
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Remplir l'écran avec du blanc
    ecran.fill(white)

    # Dessiner le titre
    draw_text("DRAWWY", font, black, ecran, (largeur, hauteur)[0]//2 , 200)

    # Dessiner les boutons
    buttons = ["ONLINE", "HISTOIRE", "QUITTER"]
    button_y_start = 400
    button_height = 100
    button_width = 500
    button_x = ((largeur, hauteur)[0] - button_width) // 2

    for i, button_text in enumerate(buttons):
        button_y = button_y_start + i*1.4 * button_height
        pygame.draw.rect(ecran, gray, (button_x, button_y, button_width, button_height), border_radius=100)
        draw_text(button_text, small_font, black, ecran, button_x + button_width // 2, button_y + button_height // 2)

    # Mettre à jour l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
sys.exit()
