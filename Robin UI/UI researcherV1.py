import pygame
pygame.init()

def UIresearcher():
    # Définir les dimensions de la fenêtre
    largeur, hauteur = 1200, 700
    ecran = pygame.display.set_mode((largeur, hauteur))
    pygame.display.set_caption("UIresearcher")
    
    # Couleurs
    NOIR = (0, 0, 0)
    BLANC = (255, 255, 255)
    
    # Définition des zones avec des proportions exactes
    liste_personnes = pygame.Rect(10, 10, 250, 500)
    mot_a_deviner = pygame.Rect(10, 520, 250, 170)
    zone_dessin = pygame.Rect(270, 10, 810, 680)
    chat = pygame.Rect(1090, 10, 100, 680)
    
    # Police pour les textes
    police = pygame.font.Font(None, 20)
    
    running = True
    while running:
        ecran.fill(BLANC)
        
        # Dessiner les zones avec des bords noirs
        pygame.draw.rect(ecran, BLANC, liste_personnes)
        pygame.draw.rect(ecran, NOIR, liste_personnes, 1)
        
        pygame.draw.rect(ecran, BLANC, mot_a_deviner)
        pygame.draw.rect(ecran, NOIR, mot_a_deviner, 1)
        
        pygame.draw.rect(ecran, BLANC, zone_dessin)
        pygame.draw.rect(ecran, NOIR, zone_dessin, 1)
        
        pygame.draw.rect(ecran, BLANC, chat)
        pygame.draw.rect(ecran, NOIR, chat, 1)
        
        # Ajouter les textes des titres
        texte_liste = police.render("Liste des personnes", True, NOIR)
        ecran.blit(texte_liste, (liste_personnes.x + 10, liste_personnes.y + 5))
        
        texte_mot = police.render("Mot à deviner", True, NOIR)
        ecran.blit(texte_mot, (mot_a_deviner.x + 10, mot_a_deviner.y + 5))
        
        texte_dessin = police.render("Zone de dessin", True, NOIR)
        ecran.blit(texte_dessin, (zone_dessin.x + 10, zone_dessin.y + 5))
        
        texte_chat = police.render("Chat", True, NOIR)
        ecran.blit(texte_chat, (chat.x + 10, chat.y + 5))
        
        # Rafraîchir l'écran
        pygame.display.flip()
        
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
    
    pygame.quit()

if __name__ == "__main__":
    UIresearcher()