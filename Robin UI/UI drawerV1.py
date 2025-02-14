import pygame
pygame.init()
def UIdrawer(): 
    # Dimensions de la fenêtre
    largeur, hauteur = 0, 0
    ecran = pygame.display.set_mode((largeur, hauteur))
    pygame.display.set_caption("UIdrawer")

    # Couleurs
    NOIR = (0, 0, 0)
    BLANC = (255, 255, 255)


    zones = [
        (17.7, 4.17, 44.27, 72.5),  # Zone de dessin
        (1, 4.17, 17.18, 58.33),   # Liste personnes
        (1,64.17, 17.18, 12.5),   # Mot à deviner
        (63, 4.17, 17.18, 25),  # Couleurs
        (63, 30.83, 17.18, 8.33),  # Style de stylo
        (63, 40.83, 17.18, 35.83), # Chat
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
UIdrawer()