from SoloGame.pages.theme_choicer import theme_choicer
from SoloGame.pages.image_selector import image_selector
from SoloGame.pages.play import SoloPlay
from SoloGame.comparaison import compare_images
from SoloGame.pages.image_comparaison import popup_result
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
        elif soloPage == "play":
            screen, soloPage, draw = SoloPlay(screen, cursor, theme, image, achievements_manager).run() 
        elif soloPage == "exit":
            return screen, "home"
        elif soloPage == "results":
            temp_path = "sources/SoloGame/temp/temp_draw.png"
            pygame.image.save(draw, temp_path)

            # Comparer l'image sauvegardée avec l'image de référence
            similarity_score = compare_images(f"assets/soloImages/{theme['path']}{theme['images'][image]['path']}", temp_path)
            screen = popup_result(similarity_score,screen)
            return screen, "home"
           


if __name__ == '__main__':
    W, H = pygame.display.Info().current_w, pygame.display.Info().current_h()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    soloGame(screen)
