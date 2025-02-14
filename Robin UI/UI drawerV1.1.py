import json
import pygame
from pygame.locals import *
import random
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
        #texte dans la liste de personnes:
        police = pygame.font.SysFont("serif " ,20)
        image_texte = police.render ( "Liste de joueurs:", 1 , (0,0,0) )
        ecran.blit(image_texte, (5/100*largeur,7/100*hauteur))








        #texte dans mot a deviner
        police = pygame.font.SysFont("serif " ,20)
        image_texte = police.render ( "Mot à faire deviner:", 1 , (0,0,0) )
        ecran.blit(image_texte, (5/100*largeur,77/100*hauteur))

        phrase = "Un pingouin en rollers"
        if len(phrase) <=24:
            long = int(24/len(phrase)*16)
            police = pygame.font.SysFont("monospace" ,long)
            image_texte = police.render ( phrase, 1 , (0,0,0) )
            ecran.blit(image_texte, (3/100*largeur,84/100*hauteur))
        elif len (phrase)<=48:
            long = int(48/len(phrase)*14)
            taille2parties = len(phrase)//2

            police = pygame.font.SysFont("monospace" ,long)
            image_texte = police.render ( phrase[0:taille2parties], 1 , (0,0,0) )
            ecran.blit(image_texte, (3/100*largeur,82/100*hauteur))
            image_texte2 = police.render ( phrase[taille2parties:], 1 , (0,0,0) )
            ecran.blit(image_texte2, (3/100*largeur,86/100*hauteur))
        else:
            long = int(72/len(phrase)*14)
            taille3parties = len(phrase)//3

            police = pygame.font.SysFont("monospace" ,long)
            image_texte = police.render ( phrase[0:taille3parties], 1 , (0,0,0) )
            ecran.blit(image_texte, (3/100*largeur,80/100*hauteur))
            image_texte2 = police.render ( phrase[taille3parties:taille3parties*2], 1 , (0,0,0) )
            ecran.blit(image_texte2, (3/100*largeur,84/100*hauteur))
            image_texte3 = police.render ( phrase[taille3parties*2:], 1 , (0,0,0) )
            ecran.blit(image_texte3, (3/100*largeur,88/100*hauteur))



        #dessine les contours
        for x, y, w, h in zones:
            pygame.draw.rect(ecran, NOIR, (x, y, w, h), 2)
        
        pygame.display.flip()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running=False
    

    pygame.quit()
UIdrawer()