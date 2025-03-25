from pyexpat import model

from imageio import save
from SoloGame.pages.theme_choicer import theme_choicer
from SoloGame.pages.image_selector import image_selector
from SoloGame.pages.play import SoloPlay
from shared.utils.data_manager import *
import pygame

def soloGame(screen, cursor, achievements_manager):
    soloPage = "themes"
    pygame.display.set_caption(f"Drawwy - Mode Solo")

    while True:
        if soloPage == "themes":
            screen, soloPage, theme = theme_choicer(screen, cursor)
        elif soloPage == "images":
            screen, soloPage, image = image_selector(screen, cursor, theme)
            model_path = f"assets/soloImages/{theme['path']}{theme['images'][image]['path']}"
        elif soloPage == "play":
            SoloPlay(screen, cursor, model_path, achievements_manager).run() 
        elif soloPage == "exit":
            return screen, "home"