import pygame
# par la même occasion cela importe pygame.locals dans l'espace de nom de Pygame

pygame.init()

ecran = pygame.display.set_mode((0, 0))

continuer = True

while continuer:
    ecran.fill((255, 255, 255))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            continuer = False

pygame.quit()