from pyexpat import model

from imageio import save
from SoloGame.pages.theme_choicer import theme_choicer
from SoloGame.pages.image_selector import image_selector
from SoloGame.pages.play import SoloPlay
from shared.utils.data_manager import *
import pygame


def soloGame(screen, cursor, achievements_manager):
    """
    Lance le mode Solo.

    Ce mode permet de reproduire des images du jeu en mode solo.
    Il comprend plusieurs pages :
    - "themes" : page de sélection du thème
    - "images" : page de sélection de l'image
    - "play" : page de dessin
    - "exit" : page de fin de jeu

    :param screen: L'écran de jeu.
    :type screen: pygame.Surface
    :param cursor: Le curseur de la souris.
    :type cursor: CustomCursor
    :param achievements_manager: Le gestionnaire des succès.
    :type achievements_manager: AchievementsManager
    :return: L'écran de jeu et la page suivante.
    :rtype: tuple
    """
    soloPage = "themes"
    pygame.display.set_caption(f"Drawwy - Mode Solo")

    while True:
        if soloPage == "themes":
            screen, soloPage, theme = theme_choicer(screen, cursor)
        elif soloPage == "images":
            screen, soloPage, image = image_selector(screen, cursor, theme)
        elif soloPage == "play":
            model_path = f"assets/soloImages/{
                theme['path']}{
                theme['images'][image]['path']}"
            SoloPlay(screen, cursor, model_path, achievements_manager)
            soloPage = "exit"
        elif soloPage == "exit":
            return screen, "home"
