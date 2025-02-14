import pygame
pygame.init()

def UIresearcher(): 
    # Dimensions de la fenêtre
    largeur, hauteur = 0, 0
    ecran = pygame.display.set_mode((largeur, hauteur))
    pygame.display.set_caption("UIresearcher")

    # Couleurs
    NOIR = (0, 0, 0)
    BLANC = (255, 255, 255)


    zones = [
        (340, 50, 850, 870),  # Zone de dessin
        (20, 50, 300, 700),   # Liste personnes
        (20,770, 300, 150),   # Mot à deviner
        (1210, 50, 300, 870), # Chat
    ]


    running = True
    while running:
        ecran.fill(BLANC)


        for x, y, w, h in zones:
            pygame.draw.rect(ecran, NOIR, (x, y, w, h), 2)

        pygame.display.flip()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
UIresearcher()