import pygame
pygame.init()
def UIdrawer(): 
    info_ecran = pygame.display.Info()
    largeur, hauteur = info_ecran.current_w, info_ecran.current_h
    # Dimensions de la fenêtre
    ecran = pygame.display.set_mode((largeur, hauteur))
    pygame.display.set_caption("UIdrawer")

    # Couleurs
    NOIR = (0, 0, 0)
    BLANC = (255, 255, 255)


    zones = [
        (20/100*largeur, 4.17/100*hauteur, 60/100*largeur, 91/100*hauteur),  # Zone de dessin
        (1/100*largeur, 4.17/100*hauteur, 18/100*largeur, 70/100*hauteur),   # Liste personnes
        (1/100*largeur,75/100*hauteur, 18/100*largeur, 20/100*hauteur),   # Mot à deviner
        (81/100*largeur, 4.17/100*hauteur, 18/100*largeur, 25/100*hauteur),  # Couleurs
        (81/100*largeur, 30.83/100*hauteur, 18/100*largeur, 8.33/100*hauteur),  # Style de stylo
        (81/100*largeur, 40.83/100*hauteur, 18/100*largeur, 54.5/100*hauteur), # Chat
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