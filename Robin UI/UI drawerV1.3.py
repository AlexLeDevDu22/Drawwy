import json
import pygame
pygame.init()
from pygame.locals import *
import tools
import io
from PIL import Image, ImageFilter


def UIdrawer(phrase): 
    
    drawing = False  # Indique si on est en train de dessiner
    last_pos = None  # Dernière position de la souris



    info_ecran = pygame.display.Info()
    largeur, hauteur = info_ecran.current_w, info_ecran.current_h
    # Dimensions de la fenêtre
    
    ecran = pygame.display.set_mode((largeur, hauteur))
    pygame.display.set_caption("UIdrawer")

    # Couleurs
    NOIR = (0, 0, 0)
    BLANC = (255, 255, 255)
    BEIGE = (250, 240, 230)
    VERT = (0,255,0)
    ROUGE= (255,0,0)
    BLEU= (0,0,255)
    JAUNE=(255,255,0)
    MAGENTA=(255,0,255)
    CYAN=(0,255,255)
    ecran.fill(BEIGE)
    zones = [
        (20/100*largeur, 4/100*hauteur, 60/100*largeur, 91/100*hauteur),  # Zone de dessin
        (1/100*largeur, 4/100*hauteur, 18/100*largeur, 70/100*hauteur),   # Liste personnes
        (1/100*largeur,75/100*hauteur, 18/100*largeur, 20/100*hauteur),   # Mot à deviner
        (81/100*largeur, 4/100*hauteur, 18/100*largeur, 25/100*hauteur),  # Couleurs
        (81/100*largeur, 30.83/100*hauteur, 18/100*largeur, 8.33/100*hauteur),  # Style de stylo
        (81/100*largeur, 40.83/100*hauteur, 18/100*largeur, 54.5/100*hauteur), # Chat
        (1/100*largeur, 4/100*hauteur, 18/100*largeur, 7/100*hauteur), #Texte joueurs
        (1/100*largeur, 11/100*hauteur, 18/100*largeur, 7/100*hauteur),#p1
        (1/100*largeur, 18/100*hauteur, 18/100*largeur, 7.1/100*hauteur),#p2
        (1/100*largeur, 25/100*hauteur, 18/100*largeur, 7/100*hauteur),#p3
        (1/100*largeur, 32/100*hauteur, 18/100*largeur, 7/100*hauteur),#p4
        (1/100*largeur, 39/100*hauteur, 18/100*largeur, 7/100*hauteur),#p5
        (1/100*largeur, 46/100*hauteur, 18/100*largeur, 7/100*hauteur),#p6
        (1/100*largeur, 53/100*hauteur, 18/100*largeur, 7.1/100*hauteur),#p7
        (1/100*largeur, 60/100*hauteur, 18/100*largeur, 7/100*hauteur),#p8
        (1/100*largeur, 67/100*hauteur, 18/100*largeur, 7/100*hauteur),#p9

    ]
    

    running = True
    while running:
        
        
        pygame.draw.rect(ecran, BLANC,(1/100*largeur, 4/100*hauteur, 18/100*largeur, 70/100*hauteur) )
        pygame.draw.rect(ecran, BLANC,(81/100*largeur, 4/100*hauteur, 18/100*largeur, 25/100*hauteur) )
        pygame.draw.rect(ecran, BLANC,(81/100*largeur, 30.83/100*hauteur, 18/100*largeur, 8.33/100*hauteur) )
        pygame.draw.rect(ecran, BLANC,(81/100*largeur, 40.83/100*hauteur, 18/100*largeur, 54.5/100*hauteur) )


        #texte dans la liste de personnes:
        police = pygame.font.Font("PermanentMarker.ttf" ,20)
        image_texte = police.render ( "Liste de joueurs:", 1 , (0,0,0) )
        ecran.blit(image_texte, (5.5/100*largeur,6/100*hauteur))

        for i in range(1,10):
            tools.banniere(i,"Caca",JAUNE,3,False)

        
        #texte dans mot a deviner
        pygame.draw.rect(ecran, VERT,(1/100*largeur,75/100*hauteur, 18/100*largeur, 20/100*hauteur) )

        police = pygame.font.Font("PermanentMarker.ttf" ,20)
        image_texte = police.render ( "Mot à faire deviner:", 1 , (0,0,0) )
        ecran.blit(image_texte, (5/100*largeur,77/100*hauteur))

    
        if len(phrase) <=24:
            long = int(24/len(phrase)*16)
            police = pygame.font.Font("PermanentMarker.ttf" ,long)
            image_texte = police.render ( phrase, 1 , (0,0,0) )
            ecran.blit(image_texte, (3/100*largeur,84/100*hauteur))
        elif len (phrase)<=48:
            long = int(48/len(phrase)*14)
            taille2parties = len(phrase)//2

            police = pygame.font.Font("PermanentMarker.ttf" ,long)
            image_texte = police.render ( phrase[0:taille2parties], 1 , (0,0,0) )
            ecran.blit(image_texte, (3/100*largeur,82/100*hauteur))
            image_texte2 = police.render ( phrase[taille2parties:], 1 , (0,0,0) )
            ecran.blit(image_texte2, (3/100*largeur,86/100*hauteur))
        else:
            long = int(72/len(phrase)*14)
            taille3parties = len(phrase)//3

            police = pygame.font.Font("PermanentMarker.ttf" ,long)
            image_texte = police.render ( phrase[0:taille3parties], 1 , (0,0,0) )
            ecran.blit(image_texte, (3/100*largeur,80/100*hauteur))
            image_texte2 = police.render ( phrase[taille3parties:taille3parties*2], 1 , (0,0,0) )
            ecran.blit(image_texte2, (3/100*largeur,84/100*hauteur))
            image_texte3 = police.render ( phrase[taille3parties*2:], 1 , (0,0,0) )
            ecran.blit(image_texte3, (3/100*largeur,88/100*hauteur))



        #dessine les contours
        for x, y, w, h in zones:
            pygame.draw.rect(ecran, NOIR, (x, y, w, h), 1)
        
        pygame.display.flip()


        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running=False
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                last_pos = event.pos  # Mémoriser la première position

         # Mouvement de la souris avec le bouton enfoncé
            if event.type == pygame.MOUSEMOTION and drawing:
                pygame.draw.line(ecran, ROUGE, last_pos, event.pos, 3)  # Tracer une ligne
                last_pos = event.pos  # Mettre à jour la position
                pygame.display.flip()  # Mettre à jour l'affichage après chaque ligne

            # Fin du dessin (bouton relâché)
            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
    

    pygame.quit()
test = tools.get_random_sentence()
UIdrawer(test)