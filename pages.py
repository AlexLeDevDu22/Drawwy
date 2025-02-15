import pygame
import sys
import tools
import gameVar

#*pygame
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
BLEU_CLAIR = pygame.Color('lightskyblue3')
BLEU = pygame.Color('dodgerblue2')

def input_pseudo():
    """Affiche une fenêtre pour entrer le pseudo"""
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Entrez votre pseudo")
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(100, 80, 200, 40)
    text = ''
    active = True
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(BLANC)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and text.strip():
                    pygame.quit()
                    return text  # Retourne le pseudo saisi
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        # Mise à jour visuelle
        color = BLEU if active else BLEU_CLAIR
        txt_surface = font.render(text, True, NOIR)
        input_box.w = max(200, txt_surface.get_width() + 10)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)


        
def UIdrawer(): 
    pygame.init()
    
    largeur, hauteur = tools.get_screen_size()
    # Dimensions de la fenêtre
    screen = pygame.display.set_mode((largeur, hauteur))
    pygame.display.set_caption("UIdrawer")
    clock = pygame.time.Clock()
    clock.tick(1)

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
        
        
        #! background
        
        screen.fill(BEIGE)
        pygame.draw.rect(screen, BLANC,(20/100*largeur, 4/100*hauteur, 60/100*largeur, 91/100*hauteur) )
        pygame.draw.rect(screen, BLANC,(1/100*largeur, 4/100*hauteur, 18/100*largeur, 70/100*hauteur) )
        pygame.draw.rect(screen, BLANC,(81/100*largeur, 4/100*hauteur, 18/100*largeur, 25/100*hauteur) )
        pygame.draw.rect(screen, BLANC,(81/100*largeur, 30.83/100*hauteur, 18/100*largeur, 8.33/100*hauteur) )
        pygame.draw.rect(screen, BLANC,(81/100*largeur, 40.83/100*hauteur, 18/100*largeur, 54.5/100*hauteur) )
        
        
        

        #! texte dans la liste de personnes:
        police = pygame.font.SysFont("serif " ,20)
        image_texte = police.render ( "Liste de joueurs:", 1 , (0,0,0) )
        screen.blit(image_texte, (5.5/100*largeur,6/100*hauteur))

        for y,player in enumerate(gameVar.PLAYERS):
            tools.banniere(screen,y+1, player["pseudo"], JAUNE, 3, True)


        #dessine les contours
        for x, y, w, h in zones:
            pygame.draw.rect(screen, NOIR, (x, y, w, h), 1)

        #! texte dans mot a deviner
        pygame.draw.rect(screen, VERT,(1/100*largeur,75/100*hauteur, 18/100*largeur, 20/100*hauteur) )

        police = pygame.font.SysFont("serif " ,20)
        image_texte = police.render ( "Mot à faire deviner:", 1 , (0,0,0) )
        screen.blit(image_texte, (5/100*largeur,77/100*hauteur))

    
        if len(gameVar.CURRENT_SENTENCE) >0:
            if len(gameVar.CURRENT_SENTENCE) <=24:
                long = int(24/len(gameVar.CURRENT_SENTENCE)*16)
                police = pygame.font.SysFont("monospace" ,long)
                image_texte = police.render ( gameVar.CURRENT_SENTENCE, 1 , (0,0,0) )
                screen.blit(image_texte, (3/100*largeur,84/100*hauteur))
            elif len (gameVar.CURRENT_SENTENCE)<=48:
                long = int(48/len(gameVar.CURRENT_SENTENCE)*14)
                taille2parties = len(gameVar.CURRENT_SENTENCE)//2

                police = pygame.font.SysFont("monospace" ,long)
                image_texte = police.render ( gameVar.CURRENT_SENTENCE[0:taille2parties], 1 , (0,0,0) )
                screen.blit(image_texte, (3/100*largeur,82/100*hauteur))
                image_texte2 = police.render ( gameVar.CURRENT_SENTENCE[taille2parties:], 1 , (0,0,0) )
                screen.blit(image_texte2, (3/100*largeur,86/100*hauteur))
            else:
                long = int(72/len(gameVar.CURRENT_SENTENCE)*14)
                taille3parties = len(gameVar.CURRENT_SENTENCE)//3

                police = pygame.font.SysFont("monospace" ,long)
                image_texte = police.render ( gameVar.CURRENT_SENTENCE[0:taille3parties], 1 , (0,0,0) )
                screen.blit(image_texte, (3/100*largeur,80/100*hauteur))
                image_texte2 = police.render ( gameVar.CURRENT_SENTENCE[taille3parties:taille3parties*2], 1 , (0,0,0) )
                screen.blit(image_texte2, (3/100*largeur,84/100*hauteur))
                image_texte3 = police.render ( gameVar.CURRENT_SENTENCE[taille3parties*2:], 1 , (0,0,0) )
                screen.blit(image_texte3, (3/100*largeur,88/100*hauteur))

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.QUIT:
                    running=False
                    
        pygame.display.flip()