import pygame
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

pygame.font.init()
font = pygame.font.Font(None, 24)

def afficher_texte(surface, texte, position):
    texte_rendu = font.render(texte, True, NOIR)
    surface.blit(texte_rendu, position)