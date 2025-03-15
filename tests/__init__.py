from theme_choicer import theme_choicer
from image_selector import image_selector
from soloGame import SoloGame

import pygame

def SoloMode(screen):
    soloPage="theme"
    while True:
        if soloPage=="theme":
            screen, soloPage=theme_choicer(screen)
        elif soloPage=="image":
            screen, soloPage=image_selector(screen)
        elif soloPage=="image":
            screen, soloPage=SoloGame(screen)
        elif soloPage=="exit":
            return screen, "home"
            

if __name__ == '__main__':
    W, H = pygame.display.Info().current_w, pygame.display.Info().current_h()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    SoloMode(screen)