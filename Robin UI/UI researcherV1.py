import pygame
pygame.init()

def UIresearcher():
    # Récupérer les dimensions de l'écran
    info_ecran = pygame.display.Info()
    largeur, hauteur = info_ecran.current_w, info_ecran.current_h
    ecran = pygame.display.set_mode((largeur, hauteur), pygame.FULLSCREEN)
    pygame.display.set_caption("UIresearcher")
    
    # Couleurs
    NOIR = (0, 0, 0)
    BLANC = (255, 255, 255)
    
    # Paramètres des marges et espacement
    marge_gauche = int(largeur * 0.01)
    marge_droite = int(largeur * 0.01)
    marge_haut = int(hauteur * 0.04)
    marge_bas = int(hauteur * 0.04)
    espacement = int(largeur * 0.01)
    
    # Calcul des dimensions des zones
    largeur_disponible = largeur - marge_gauche - marge_droite - 2 * espacement
    hauteur_disponible = hauteur - marge_haut - marge_bas
    
    # Largeurs relatives des zones
    ratio_liste = 0.15
    ratio_dessin = 0.65
    ratio_chat = 0.20
    
    # Calcul des dimensions réelles
    largeur_liste = int(largeur_disponible * ratio_liste)
    largeur_dessin = int(largeur_disponible * ratio_dessin)
    largeur_chat = largeur_disponible - largeur_liste - largeur_dessin
    
    hauteur_liste_principale = int(hauteur_disponible * 0.82)
    hauteur_mot_a_deviner = hauteur_disponible - hauteur_liste_principale
    
    # Définition des zones (x, y, largeur, hauteur)
    zones = [
        # Zone de dessin (centre)
        (marge_gauche + largeur_liste + espacement, marge_haut, 
         largeur_dessin, hauteur_disponible),
        
        # Liste personnes (gauche haut)
        (marge_gauche, marge_haut, 
         largeur_liste, hauteur_liste_principale),
        
        # Mot à deviner (gauche bas)
        (marge_gauche, marge_haut + hauteur_liste_principale, 
         largeur_liste, hauteur_mot_a_deviner),
        
        # Chat (droite)
        (marge_gauche + largeur_liste + espacement + largeur_dessin + espacement, marge_haut,
         largeur_chat, hauteur_disponible)
    ]
    
    police = pygame.font.Font(None, 36)
    textes = ["Zone de dessin", "Liste des personnes", "Mot à deviner", "Chat"]
    
    running = True
    while running:
        ecran.fill(BLANC)
        
        # Dessiner les zones
        for i, (x, y, w, h) in enumerate(zones):
            pygame.draw.rect(ecran, NOIR, (x, y, w, h), 2)
            
            # Afficher les textes pour identifier chaque zone
            texte_surface = police.render(textes[i], True, NOIR)
            ecran.blit(texte_surface, (x + 10, y + 10))
        
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