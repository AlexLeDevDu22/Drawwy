import pygame
pygame.init()
from PIL import Image, ImageFilter
import io
import Fonction


<<<<<<< HEAD
def flou(phrase, blur_radius=3.5):
    width, height = phrase.get_size()
    image_str = pygame.image.tostring(phrase, "RGBA")
=======
def flou(pygame_surface, blur_radius=3.5):
    width, height = pygame_surface.get_size()
    image_str = pygame.image.tostring(pygame_surface, "RGBA")
>>>>>>> 4c2ce9a86c592a46523fea2968c84f0da9d219bb
    image_pil = Image.frombytes("RGBA", (width, height), image_str)
    blurred_pil = image_pil.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred_str = blurred_pil.tobytes()
    blurred_surface = pygame.image.fromstring(blurred_str, (width, height), "RGBA")
<<<<<<< HEAD
    return blurred_surface


=======

    return blurred_surface
>>>>>>> 4c2ce9a86c592a46523fea2968c84f0da9d219bb
def UIresearcher(phrase,trouver): 
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
        (81/100*largeur, 4.17/100*hauteur, 18/100*largeur, 91/100*hauteur), # Chat
    ]


    running = True
    while running:
        ecran.fill(BLANC)

        #texte dans mot a deviner  
<<<<<<< HEAD
        police = pygame.font.SysFont("serif " ,20)
        image_texte = police.render ( "Phrase à trouver:", 1 , (0,0,0) )
        ecran.blit(image_texte, (5/100*largeur,77/100*hauteur))

=======
>>>>>>> 4c2ce9a86c592a46523fea2968c84f0da9d219bb
        if len(phrase) <=24:
            long = int(24/len(phrase)*16)
            police = pygame.font.SysFont("monospace" ,long)
            image_texte = police.render ( phrase, 1 , (0,0,0) )
            if trouver==False:
                image_texte= flou(image_texte)
            ecran.blit(image_texte, (3/100*largeur,84/100*hauteur))
        elif len (phrase)<=48:
            long = int(48/len(phrase)*14)
            taille2parties = len(phrase)//2
            police = pygame.font.SysFont("monospace" ,long)
            image_texte = police.render ( phrase[0:taille2parties], 1 , (0,0,0) )
            image_texte2 = police.render ( phrase[taille2parties:], 1 , (0,0,0) )
            if trouver==False:
                image_texte=flou(image_texte)
                image_texte2=flou(image_texte2)
            ecran.blit(image_texte, (3/100*largeur,82/100*hauteur))
            ecran.blit(image_texte2, (3/100*largeur,86/100*hauteur))
        else:
            long = int(72/len(phrase)*14)
            taille3parties = len(phrase)//3
            police = pygame.font.SysFont("monospace" ,long)
            image_texte = police.render ( phrase[0:taille3parties], 1 , (0,0,0) )
            image_texte2 = police.render ( phrase[taille3parties:taille3parties*2], 1 , (0,0,0) )
            image_texte3 = police.render ( phrase[taille3parties*2:], 1 , (0,0,0) )
            if trouver==False:
                image_texte=flou(image_texte)
                image_texte2=flou(image_texte2)
                image_texte3=flou(image_texte3)
            ecran.blit(image_texte, (3/100*largeur,80/100*hauteur))
            ecran.blit(image_texte2, (3/100*largeur,84/100*hauteur))
            ecran.blit(image_texte3, (3/100*largeur,88/100*hauteur))
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    trouver=True


<<<<<<< HEAD

=======
>>>>>>> 4c2ce9a86c592a46523fea2968c84f0da9d219bb
        for x, y, w, h in zones:
            pygame.draw.rect(ecran, NOIR, (x, y, w, h), 2)

        pygame.display.flip()

        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()



#parametres
<<<<<<< HEAD
phrase="Un pingouin en roller"
=======
phrase="Un pingouin qui fait du"
>>>>>>> 4c2ce9a86c592a46523fea2968c84f0da9d219bb
trouver=False
UIresearcher(phrase,trouver)