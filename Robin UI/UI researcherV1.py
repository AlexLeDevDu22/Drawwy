import pygame
pygame.init()

def UIresearcher():
    # Récupérer les dimensions de l'écran
    info_ecran = pygame.display.Info()
    largeur, hauteur = info_ecran.current_w, info_ecran.current_h
    
    # Créer une fenêtre en plein écran
    ecran = pygame.display.set_mode((largeur, hauteur), pygame.FULLSCREEN)
    pygame.display.set_caption("UIresearcher")
    
    # Couleurs
    NOIR = (0, 0, 0)
    BLANC = (255, 255, 255)
    
    # Calcul des proportions adaptées à la taille de l'écran
    largeur_liste = int(largeur * 0.17)  # environ 17% de la largeur
    largeur_chat = int(largeur * 0.15)   # environ 15% de la largeur
    espacement = int(largeur * 0.01)     # 1% pour les marges
    
    largeur_dessin = largeur - largeur_liste - largeur_chat - espacement * 3
    
    hauteur_liste_principale = int(hauteur * 0.75)
    hauteur_mot = hauteur - hauteur_liste_principale - espacement * 2
    
    # Définition des zones avec les proportions calculées
    marge = espacement
    liste_personnes = pygame.Rect(marge, marge, 
                                 largeur_liste, 
                                 hauteur_liste_principale)
    
    mot_a_deviner = pygame.Rect(marge, 
                               marge + hauteur_liste_principale + espacement, 
                               largeur_liste, 
                               hauteur_mot)
    
    zone_dessin = pygame.Rect(marge + largeur_liste + espacement, 
                             marge, 
                             largeur_dessin, 
                             hauteur - marge * 2)
    
    chat = pygame.Rect(marge + largeur_liste + largeur_dessin + espacement * 2, 
                      marge, 
                      largeur_chat, 
                      hauteur - marge * 2)
    
    # Police pour les textes (taille adaptée à la résolution)
    taille_police = max(16, int(hauteur * 0.025))
    police = pygame.font.SysFont("Arial", taille_police)
    
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