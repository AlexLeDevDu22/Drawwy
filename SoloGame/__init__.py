from SoloGame.pages.theme_choicer import theme_choicer
from SoloGame.pages.image_selector import image_selector
from SoloGame.pages.play import SoloPlay

import pygame

def soloGame(screen):
    soloPage="theme"
    while True:
        if soloPage=="theme":
            screen, soloPage, theme, difficulty=theme_choicer(screen)
        elif soloPage=="image":
            screen, soloPage=image_selector(screen, theme, difficulty)
        elif soloPage=="image":
            screen, soloPage=SoloPlay(screen)
        elif soloPage=="exit":
            return screen, "home"
                
if __name__ == '__main__':
    W, H = pygame.display.Info().current_w, pygame.display.Info().current_h()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    soloGame(screen)