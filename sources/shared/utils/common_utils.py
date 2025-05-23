from shared.ui.common_ui import *
from shared.utils.data_manager import *

import pygame
import os


def draw_text(text, font, color, surface, x, y, shadow=False):
    """
    Dessine un texte sur une surface pygame.

    Args:
        text (str): Le texte  souhaite.
        font (pygame.font.Font): La police du texte.
        color (tuple): La couleur du texte.
        surface (pygame.Surface): La surface sur laquelle dessiner le texte.
        x (int): La coordon ne x du centre du texte.
        y (int): La coordon ne y du centre du texte.
        shadow (bool): Si True, dessine une ombre grise derri re le texte.
    """
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    if shadow:
        text_obj_shadow = font.render(text, True, DARK_GRAY)
        surface.blit(
            text_obj_shadow,
            (textrect.x + 2,
             textrect.y + 2))  # Ombre
    surface.blit(textobj, textrect)


class AchievementManager:

    def __init__(self, W, H):
        # dessiner la boite
        """
        Initialize the AchievementManager with screen dimensions and set initial states.

        Args:
            W (int): The width of the screen.
            H (int): The height of the screen.
        """

        self.width = 500
        self.height = 100
        self.W = W
        self.H = H
        self.popup_active = False
        self.start_time = pygame.time.get_ticks()

    def new_achievement(self, index):
        """
        Mark an achievement as succeeded and activate the achievement popup.

        Args:
            index (int): The index of the achievement to be marked as succeeded.
        """

        self.current_achievement = PLAYER_DATA["achievements"][index]
        if not self.current_achievement["succeed"]:
            PLAYER_DATA["achievements"][index]["succeed"] = True
            save_data("PLAYER_DATA")
            self.popup_active = True
            self.start_time = pygame.time.get_ticks()

    def draw_popup_if_active(self, screen):
        """
        Draw an achievement popup if one is active.

        The popup will be drawn for 5 seconds, with an animation that slides it in from the right.

        Args:
            screen (pygame.display): The screen to draw the popup on.

        """
        if self.popup_active:
            if self.start_time + 5000 < pygame.time.get_ticks():
                self.popup_active = False
            anim_offset = 0

            if self.start_time + 4000 > pygame.time.get_ticks():
                anim_offset = (self.width + 50) * min((pygame.time.get_ticks() - \
                               self.start_time) / 1000, 1) - (self.width + 50)
            else:
                anim_offset = (self.width + 50) * max((self.start_time + 5000 - \
                               pygame.time.get_ticks()) / 1000, 0) - (self.width + 50)

            box_rect_achievement = pygame.Rect(
                50 + anim_offset, self.H - 230, self.width, self.height)
            pygame.draw.rect(
                screen,
                PASTEL_GREEN,
                box_rect_achievement,
                border_radius=15)
            # rond valide
            pygame.draw.circle(
                screen,
                DARK_BLUE,
                (100 +
                 anim_offset,
                 self.H -
                 240 +
                 self.height //
                 2),
                20)
            pygame.draw.line(
                screen,
                WHITE,
                (90 +
                 anim_offset,
                 self.H -
                 240 +
                 self.height //
                 2),
                (100 +
                 anim_offset,
                 self.H -
                 240 +
                 self.height //
                 2 +
                 10),
                4)
            pygame.draw.line(
                screen,
                WHITE,
                (100 +
                 anim_offset,
                 self.H -
                 240 +
                 self.height //
                 2 +
                 10),
                (115 +
                 anim_offset,
                 self.H -
                 240 +
                 self.height //
                 2 -
                 10),
                4)

            # dessiner le texte
            draw_text(
                self.current_achievement["title"],
                SMALL_FONT,
                BLACK,
                screen,
                50 +
                anim_offset +
                self.width //
                2,
                self.H -
                245 +
                self.height //
                2)
            draw_text(
                self.current_achievement["explication"],
                SMALL_FONT,
                ORANGE,
                screen,
                50 +
                anim_offset +
                self.width //
                2,
                self.H -
                205 +
                self.height //
                2)


class CustomCursor:
    def __init__(self, cursor_path):
        """
        Initialize the custom cursor.

        :param cursor_path: The path to the image representing the normal state of the cursor.
        :type cursor_path: str

        :raises FileNotFoundError: If the image at `cursor_path` does not exist.
        """
        self.custom_cursor = bool(cursor_path)
        pygame.mouse.set_visible(not self.custom_cursor)

        if self.custom_cursor:
            self.cursor_default = pygame.transform.scale(
                pygame.image.load(cursor_path).convert_alpha(), (32, 32)
            )
            self.as_pressed_cursor = False
            clicked_path = cursor_path[:-4] + "_clicked" + cursor_path[-4:]
            if os.path.exists(clicked_path):
                self.cursor_pressed = pygame.transform.scale(
                    pygame.image.load(clicked_path).convert_alpha(), (32, 32)
                )
                self.as_pressed_cursor = True

    def show(self, screen, mouse_pos=None, mouse_pressed=False):
        """
        Draw the custom cursor on the given screen at the specified mouse position.

        :param screen: The screen to draw the cursor on.
        :type screen: pygame.display
        :param mouse_pos: The mouse position to draw the cursor at. If `None`, it will be drawn at the current mouse position.
        :type mouse_pos: tuple or None
        :param mouse_pressed: If `True`, the pressed version of the cursor will be drawn if it is available.
        :type mouse_pressed: bool
        """
        if self.custom_cursor:
            if mouse_pos:
                mouse_x, mouse_y = mouse_pos
            else:
                mouse_x, mouse_y = pygame.mouse.get_pos()

            screen.blit(
                self.cursor_pressed if mouse_pressed and self.as_pressed_cursor else self.cursor_default,
                (mouse_x,
                 mouse_y))
