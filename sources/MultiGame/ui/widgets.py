import pygame
import MultiGame.utils.tools as tools
from shared.tools import show_emote
from shared.tools import apply_circular_mask
from shared.ui.common_ui import *
from shared.utils.data_manager import *

try:
    from pygame_emojis import load_emoji
except BaseException:
    import pygame.freetype

import math
import os


def timer(MultiGame):
    """
    Dessine le timer du jeu sur l'écran.

    Il y a un timer qui descend en bas de l'écran, et qui est rafraichi
    toutes les secondes. Il y a un padding un peu plus grand pour
    que le timer ne soit pas trop près de l'ecran, et qu'il soit
    plus lisible. Il y a un padding un peu plus grand pour que le timer
    ne soit pas trop près de l'ecran, et qu'il soit plus lisible.

    :param MultiGame: instance de la classe MultiGame
    :return: None
    """
    if len(MultiGame.PLAYERS) == 1:
        return

    timer_text = f"{
        MultiGame.game_remaining_time //
        60}:{
        0 if MultiGame.game_remaining_time %
        60 < 10 else ''}{
            MultiGame.game_remaining_time %
        60}"

    # Créer un texte pour le timer
    font = pygame.font.Font("assets/text_police/PermanentMarker.ttf", 25)
    text_surface = font.render(timer_text, True, (0, 0, 0))

    # Calculer la taille du rectangle (qui sera juste la taille du texte)
    text_rect = text_surface.get_rect()
    text_rect.center = (MultiGame.W // 2, 25)  # Centré en haut de l'écran

    # Dessiner le rectangle autour du texte
    rect_x = text_rect.x - 10  # Un petit padding
    rect_y = text_rect.y - 5
    rect_width = text_rect.width + 20  # Un petit padding à droite et à gauche
    rect_height = text_rect.height + 5  # Un padding en haut et en bas
    pygame.draw.rect(MultiGame.screen, (230, 0, 0),
                     (rect_x, rect_y, rect_width, rect_height))

    # Afficher le texte du timer
    MultiGame.screen.blit(text_surface, text_rect)


def players(MultiGame):
    """
    Draws the player list on the game screen.

    This function renders a list of players on the left side of the screen,
    displaying their avatars, pseudo names, and points. It highlights the current
    drawer and indicates whether a player has found the correct answer.
    The avatars can be either matrix-based or emoji-based, and the display
    adapts accordingly.

    :param MultiGame: instance of the MultiGame class
    :return: None
    """
    pygame.draw.rect(
        MultiGame.screen,
        WHITE,
        (0.01 * MultiGame.W,
         0.04 * MultiGame.H,
         0.18 * MultiGame.W,
         0.7 * MultiGame.H))
    pygame.draw.rect(
        MultiGame.screen,
        BLACK,
        (0.01 * MultiGame.W,
         0.04 * MultiGame.H,
         0.18 * MultiGame.W,
         0.7 * MultiGame.H),
        1)

    image_texte = BUTTON_FONT.render("Joueurs", 1, (0, 0, 0))
    MultiGame.screen.blit(
        image_texte,
        (4.5 / 100 * MultiGame.W,
         5.5 / 100 * MultiGame.H))

    pygame.draw.rect(
        MultiGame.screen,
        ORANGE,
        (0.01 * MultiGame.W,
         0.11 * MultiGame.H,
         0.18 * MultiGame.W,
         2))

    dico_co = [
        [(1 / 100 * MultiGame.W, (11 + i * 7) / 100 * MultiGame.H, 18 / 100 * MultiGame.W, 7 / 100 * MultiGame.H),
         (1.5 / 100 * MultiGame.W, (12 + i * 7) / 100 * MultiGame.H),
            (4.6 / 100 * MultiGame.W, (12.6 + i * 7) / 100 * MultiGame.H),
            (12.4 / 100 * MultiGame.W, (12 + i * 7) / 100 * MultiGame.H),
            (12.4 / 100 * MultiGame.W, (14 + i * 7) / 100 * MultiGame.H),
            (17.8 / 100 * MultiGame.W, (13.3 + i * 7) / 100 * MultiGame.H)]
        for i in range(9)
    ]

    for i, player in enumerate(MultiGame.PLAYERS):
        if i * 0.07 * MultiGame.H > 0.7 * MultiGame.H:
            break
        i = min(i, 8)

        # fond
        pygame.draw.rect(
            MultiGame.screen,
            (222,
             0,
             0) if player["pid"] == MultiGame.CURRENT_DRAWER else (
                0,
                0,
                0),
            dico_co[i][0])

        pygame.draw.rect(MultiGame.screen,
                         CONFIG["players_colors"][i % len(CONFIG["players_colors"])],
                         (dico_co[i][0][0] + 3,
                          dico_co[i][0][1] + 3,
                             dico_co[i][0][2] - 6,
                             dico_co[i][0][3] - 6))

        pygame.draw.rect(MultiGame.screen,
                         CONFIG["players_colors"][i % len(CONFIG["players_colors"])],
                         (dico_co[i][0][0] + 3,
                          dico_co[i][0][1] + 3,
                             dico_co[i][0][2] - 6,
                             dico_co[i][0][3] - 6))

        pygame.draw.rect(MultiGame.screen,
                         CONFIG["players_colors"][i % len(CONFIG["players_colors"])],
                         (dico_co[i][0][0] + 3,
                          dico_co[i][0][1] + 3,
                             dico_co[i][0][2] - 6,
                             dico_co[i][0][3] - 6))

        # avatar
        if player["avatar"]["type"] == "matrix":
            if player["avatar"]["has_border"]:
                if "pygame_border" not in player["avatar"].keys():
                    border = pygame.image.load(player["avatar"]["border_path"])
                    border = pygame.transform.scale(
                        border, (5 / 100 * MultiGame.H + 6, 5 / 100 * MultiGame.H + 6))
                    MultiGame.PLAYERS[i]["avatar"]["pygame_border"] = border
                MultiGame.screen.blit(
                    player["avatar"]["pygame_border"],
                    (dico_co[i][1][0] - 3,
                     dico_co[i][1][1] - 3))

            if player["avatar"]["type"] == "matrix" and (
                    "pygame_image" not in player["avatar"].keys()):
                avatar = tools.matrix_to_image(player["avatar"]["matrix"])
                avatar = pygame.transform.scale(
                    avatar, (5 / 100 * MultiGame.H, 5 / 100 * MultiGame.H))
                apply_circular_mask(avatar)
                MultiGame.PLAYERS[i]["avatar"]["pygame_image"] = avatar
            MultiGame.screen.blit(
                player["avatar"]["pygame_image"],
                dico_co[i][1])
        else:  # emoji
            pygame.draw.circle(
                MultiGame.screen,
                BLUE,
                (dico_co[i][1][0] +
                 5 /
                 100 *
                 MultiGame.H //
                 2,
                 dico_co[i][1][1] +
                    5 /
                    100 *
                    MultiGame.H //
                    2),
                5 /
                100 *
                MultiGame.H //
                2 +
                3)
            pygame.draw.circle(
                MultiGame.screen,
                player["avatar"]["color"],
                (dico_co[i][1][0] + 5 / 100 * MultiGame.H // 2,
                 dico_co[i][1][1] + 5 / 100 * MultiGame.H // 2),
                5 / 100 * MultiGame.H // 2)

            try:
                MultiGame.screen.blit(
                    load_emoji(
                        player["avatar"]["emoji"],
                        (4.6 / 100 * MultiGame.H,
                         4.6 / 100 * MultiGame.H)),
                    (dico_co[i][1][0],
                     dico_co[i][1][1] + 4))
            except BaseException:
                seguisy80 = pygame.freetype.SysFont("segoeuisymbol", 30)
                emoji, rect = seguisy80.render(
                    player["avatar"]["emoji"], "black")
                rect.center = (dico_co[i][1][0] + 20, dico_co[i][1][1] + 24)
                MultiGame.screen.blit(emoji, rect)

        # pseudo
        text_color = (
            10,
            10,
            10) if player["pid"] == MultiGame.PLAYER_ID else (
            100,
            100,
            100)
        # font = pygame.font.Font("assets/PermanentMarker.ttf" ,30)
        image_texte = MEDIUM_FONT.render(player["pseudo"], 1, text_color)
        MultiGame.screen.blit(image_texte, dico_co[i][2])
        # points
        # font = pygame.font.Font("assets/PermanentMarker.ttf" ,20)

        if player["pid"] != MultiGame.CURRENT_DRAWER and len(
                MultiGame.PLAYERS) > 1:
            # image_texte = SMALL_FONT.render ( "Trouvé ", 1 , text_color )
            # MultiGame.screen.blit(image_texte, dico_co[i][3])

            # pygame.draw.circle(MultiGame.screen, text_color, dico_co[y][4], 7)
            if player["found"]:
                pygame.draw.circle(MultiGame.screen, GREEN, dico_co[i][5], 8)
            else:
                pygame.draw.circle(MultiGame.screen, RED, dico_co[i][5], 8)

        image_texte = SMALL_FONT.render(
            str(player["points"]) + " points", 1, text_color)
        MultiGame.screen.blit(image_texte, dico_co[i][4])


def sentence(MultiGame):
    """
    Dessine le widget de la phrase à trouver sur l'écran.
    Ce widget est un rectangle qui contient le texte de la phrase à trouver.
    Si le joueur n'a pas encore trouvé la phrase, le texte est flouté.
    """
    if len(MultiGame.PLAYERS) > 1:
        pygame.draw.rect(
            MultiGame.screen,
            WHITE,
            (0.01 * MultiGame.W,
             0.75 * MultiGame.H,
             0.18 * MultiGame.W,
             0.2 * MultiGame.H))
        pygame.draw.rect(
            MultiGame.screen,
            BLACK,
            (0.01 * MultiGame.W,
             0.75 * MultiGame.H,
             0.18 * MultiGame.W,
             0.2 * MultiGame.H),
            1)

        text = "Phrase à faire deviner:"if MultiGame.me["is_drawer"] else "Phrase à trouver:"
        pygame.draw.rect(
            MultiGame.screen,
            GREEN,
            (1 / 100 * MultiGame.W,
             75 / 100 * MultiGame.H,
             18 / 100 * MultiGame.W,
             20 / 100 * MultiGame.H))

        # font = pygame.font.Font("assets/PermanentMarker.ttf" ,22)
        image_texte = SMALL_FONT.render(text, True, (0, 0, 0))
        MultiGame.screen.blit(
            image_texte,
            (2 / 100 * MultiGame.W,
             77 / 100 * MultiGame.H))

        if len(MultiGame.CURRENT_SENTENCE) > 0:
            FONT_SIZE_BASE = 20  # Taille de base de la font
            Y_START = 77 / 100 * MultiGame.H + 36  # Position de départ

            # Choisir la taille de font en fonction de la longueur du texte
            if len(MultiGame.CURRENT_SENTENCE) <= 30:
                font_size = FONT_SIZE_BASE
            elif len(MultiGame.CURRENT_SENTENCE) <= 60:
                font_size = FONT_SIZE_BASE - 2
            else:
                font_size = FONT_SIZE_BASE - 4

            lines = tools.lines_return(
                MultiGame.CURRENT_SENTENCE, MEDIUM_FONT, 0.16 * MultiGame.W)

            # Affichage ligne par ligne
            for i, ligne in enumerate(lines):
                image_texte = MEDIUM_FONT.render(
                    " " + ligne + " ", True, (20, 10, 10))
                if (not MultiGame.me["found"]
                    ) and not MultiGame.me["is_drawer"]:
                    image_texte = tools.flou(image_texte)
                MultiGame.screen.blit(
                    image_texte, (0.026 * MultiGame.W, Y_START + (i * (font_size + 2))))


def drawing(MultiGame):
    """
    Dessine le canvas et permet de dessiner dessus si le joueur est le dessinateur.

    Args:
        MultiGame (MultiGame): Le jeu.

    Returns:
        None
    """
    if not MultiGame.CANVAS:
        return

    #! show
    if MultiGame.connected and len(MultiGame.PLAYERS) > 1:
        MultiGame.screen.blit(
            MultiGame.CANVAS,
            (MultiGame.canvas_rect.x,
             MultiGame.canvas_rect.y))
    pygame.draw.rect(MultiGame.screen, BLACK, MultiGame.canvas_rect, 1)

    #! drawing
    if MultiGame.me["is_drawer"]:
        if MultiGame.canvas_rect.collidepoint(
                pygame.mouse.get_pos()):  # Vérifier si le clic est dans la zone de dessin
            # can draw
            if MultiGame.connected and len(MultiGame.PLAYERS) > 1 and 0 < MultiGame.game_remaining_time < CONFIG[
                            "game_duration"]:
                for event in MultiGame.events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        MultiGame.ALL_FRAMES = tools.split_steps_by_roll_back(
                            MultiGame.ALL_FRAMES, MultiGame.ROLL_BACK)[0]
                        MultiGame.STEP_NUM = 0
                        for frame in MultiGame.ALL_FRAMES:
                            if frame["type"] in ["new_step", "shape"]:
                                MultiGame.STEP_NUM += 1

                        MultiGame.ROLL_BACK = 0
                        MultiGame.second_draw_frames.append({"type": "new_step"})
                        MultiGame.ALL_FRAMES.append({"type": "new_step"})

                        MultiGame.achievements_manager.new_achievement(0)

                    elif MultiGame.mouse_down and event.type == pygame.MOUSEMOTION:
                        if MultiGame.lastMouseDown :
                            # Position actuelle dans le CANVAS
                            x2 = event.pos[0] - MultiGame.canvas_rect.x
                            y2 = event.pos[1] - MultiGame.canvas_rect.y

                            # Dessiner une ligne entre last_click et la position
                            # actuelle
                            if MultiGame.last_canvas_click and MultiGame.last_canvas_click != (
                                    x2, y2):
                                x1, y1 = MultiGame.last_canvas_click

                                # Générer les points entre les deux
                                MultiGame.CANVAS = tools.draw_brush_line(
                                    MultiGame.CANVAS, x1, y1, x2, y2, MultiGame.pen_color, MultiGame.pen_radius)
                                frame = {
                                    "type": "line",
                                    "x1": x1 // MultiGame.pixel_size,
                                    "y1": y1 // MultiGame.pixel_size,
                                    "x2": x2 // MultiGame.pixel_size,
                                    "y2": y2 // MultiGame.pixel_size,
                                    "color": MultiGame.pen_color,
                                    "radius": MultiGame.pen_radius}
                                MultiGame.second_draw_frames.append(frame)
                                MultiGame.ALL_FRAMES.append(frame)

                            # Mettre à jour la dernière position
                            MultiGame.last_canvas_click = (x2, y2)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        MultiGame.STEP_NUM += 1

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_z and (
                                pygame.key.get_mods() & pygame.KMOD_CTRL):  # CTRL+Z

                            MultiGame.ROLL_BACK = min(
                                MultiGame.STEP_NUM, MultiGame.ROLL_BACK + 1)

                            tools.update_canva_by_frames(
                                MultiGame, MultiGame.ALL_FRAMES, delay=False, reset=True)

                            tools.send_ws(
                                MultiGame.WS, {
                                    "header": "roll_back", "roll_back": MultiGame.ROLL_BACK})

                        # CTRL+Y
                        elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):

                            MultiGame.ROLL_BACK = max(0, MultiGame.ROLL_BACK - 1)

                            tools.update_canva_by_frames(
                                MultiGame, MultiGame.ALL_FRAMES, delay=False, reset=True)

                            tools.send_ws(
                                MultiGame.WS, {
                                    "header": "roll_back", "roll_back": MultiGame.ROLL_BACK})

        # send draw
        if MultiGame.frame_num == CONFIG["fps"] - \
                1 and MultiGame.second_draw_frames != []:
            tools.send_ws(
                MultiGame.WS, {
                    "header": "draw", "frames": tools.simplify_frames(
                        MultiGame.second_draw_frames)})  # send draw
            MultiGame.second_draw_frames = []


def slider_radius(MultiGame):
    """
    Draws a slider on the screen to adjust the pen radius.

    The slider allows users to visually adjust the pen radius used for drawing.
    It consists of a track and a movable knob that represents the current pen
    size. The knob position is updated based on user interaction. This function
    also includes a preview of the pen size.

    :param MultiGame: Instance of the MultiGame class.
    """
    pygame.draw.rect(
        MultiGame.screen,
        WHITE,
        (0.81 * MultiGame.W,
         0.3083 * MultiGame.H,
         0.18 * MultiGame.W,
         0.0833 * MultiGame.H))
    pygame.draw.rect(
        MultiGame.screen,
        BLACK,
        (0.81 *
         MultiGame.W,
         0.3083 *
         MultiGame.H,
         0.18 *
         MultiGame.W,
         0.0833 *
         MultiGame.H),
        1)

    try:
        MultiGame.pixel_size  # test la variable
    except BaseException:
        return

    slider_x, slider_y, slider_w, slider_h = (
        0.81 * MultiGame.W, 0.3083 * MultiGame.H, 0.18 * MultiGame.W, 0.0833 * MultiGame.H)
    slider_min = slider_x + 10
    slider_max = slider_x + slider_w - 10
    radius_slider_pos = slider_min + \
        (MultiGame.pen_radius // MultiGame.pixel_size - 1) * (slider_max - slider_min) / 10

    # Fond du slider
    pygame.draw.rect(MultiGame.screen, (200, 200, 200),
                     (slider_x, slider_y, slider_w, slider_h))

    # Barre de progression
    pygame.draw.line(
        MultiGame.screen,
        (0,
         0,
         0),
        (slider_min,
         slider_y +
         slider_h //
         2),
        (slider_max,
         slider_y +
         slider_h //
         2),
        4)

    # Bouton du slider
    pygame.draw.circle(MultiGame.screen, (255, 180, 50), (int(
        radius_slider_pos), slider_y + slider_h // 2 + 1), MultiGame.pen_radius)

    # Cercle de prévisualisation (taille du crayon)
    # pygame.draw.circle(MultiGame.screen, MultiGame.pen_color, (int(slider_x) - 20, int(slider_y + slider_h // 2)), MultiGame.pen_radius)

    # update
    for event in MultiGame.events:
        if event.type == pygame.MOUSEMOTION and MultiGame.mouse_down:
            if slider_min - MultiGame.pen_radius <= event.pos[0] <= slider_max + \
                    MultiGame.pen_radius and slider_y <= event.pos[1] <= slider_y + slider_h:
                radius_slider_pos = max(
                    slider_min, min(
                        event.pos[0], slider_max))
                MultiGame.pen_radius = int((int(1 +
                                                (radius_slider_pos -
                                                 slider_min) *
                                                10 /
                                                (slider_max -
                                                 slider_min))) *
                                           MultiGame.pixel_size)


def chat(MultiGame):
    """
    Draws a chat on the screen where players can send messages to each other.

    The chat consists of a box where players can type their messages and a log
    of the messages that have been sent. The chat also supports sending emotes
    which are small images that can be sent to represent an emotion.

    The chat window is divided into two parts: the top part is the log of the
    messages and the bottom part is the input box where players can type their
    messages. The log of the messages is updated in real time and can be
    scrolled up and down by the player. The input box is where players can
    type their messages and it is limited to 150 characters. When a player
    presses the send button, their message is sent to the server and it is
    added to the log of the messages.

    The chat also supports sending emotes. Emotes are small images that can be
    sent to represent an emotion. Emotes are purchased in the shop and can be
    sent by clicking on the emote icon in the chat window. When an emote is
    sent, it is added to the log of the messages.

    The chat window is updated in real time and can be moved around the screen
    by the player. The chat window is also resized when the player resizes the
    game window.

    Parameters
    ----------
    MultiGame : MultiGame
        Instance of the MultiGame class.

    """
    guess_line = tools.lines_return(
        MultiGame.guess,
        MEDIUM_FONT,
        0.15 * MultiGame.W)
    input_box = pygame.Rect(0.82 *
                            MultiGame.W, 0.9533 *
                            MultiGame.H -
                            45 -
                            len(guess_line) *
                            20, 0.16 *
                            MultiGame.W, max(40, 15 +
                                             20 *
                                             len(guess_line)))

    # Mise à jour visuelle
    min_y = 0.4083 * \
        MultiGame.H if MultiGame.me["is_drawer"] else 0.1 * MultiGame.H
    pygame.draw.rect(
        MultiGame.screen,
        WHITE,
        (0.81 *
         MultiGame.W,
         min_y,
         0.18 *
         MultiGame.W,
         0.95 *
         MultiGame.H -
         min_y))
    pygame.draw.rect(
        MultiGame.screen,
        BLACK,
        (0.81 *
         MultiGame.W,
         min_y,
         0.18 *
         MultiGame.W,
         0.95 *
         MultiGame.H -
         min_y),
        1)

    color = BLUE if MultiGame.guess_input_active else LIGHT_BLUE
    for i, line in enumerate(guess_line):
        txt_surface = MEDIUM_FONT.render(line, True, BLACK)
        MultiGame.screen.blit(
            txt_surface, (input_box.x + 5, input_box.y + 5 + i * 20))
    pygame.draw.rect(MultiGame.screen, color, input_box, 2)

    # chat
    y = 0.95 * MultiGame.H - 60 - len(guess_line) * 20 - 30

    for mess in MultiGame.MESSAGES[::-1]:
        if mess["type"] != "emote":
            if mess["type"] == "guess":
                if mess["succeed"]:

                    text = f"{
                        mess['pseudo']} à trouvé (+{
                        mess['new_points'][0]["points"]} points)!"
                    color = (0, 255, 0)

                else:

                    text = mess["message"]
                    color = (0, 0, 0)

            else:  # systeme message
                text = mess["message"]
                color = mess["color"]

            # write the message
            lines = tools.lines_return(text, MEDIUM_FONT, 0.16 * MultiGame.W)

            for line in lines[::-1]:
                if y > min_y + 16:
                    y -= 19

                    image_texte = MEDIUM_FONT.render(line, 1, color)
                    MultiGame.screen.blit(image_texte, (0.82 * MultiGame.W, y))

            if y < min_y + 18:
                break

        # emote
        elif os.path.exists("data/shop/emotes_assets/" + mess["emote_path"]):
            if y < min_y + 100:
                break
            emote_size = 150
            y -= emote_size + 20

            emote_container = pygame.Rect(
                0.83 * MultiGame.W, y, emote_size + 20, emote_size + 20)

            pygame.draw.rect(
                MultiGame.screen,
                VERY_LIGHT_BLUE,
                emote_container,
                border_radius=12)
            pygame.draw.rect(
                MultiGame.screen,
                BLACK,
                emote_container,
                1,
                border_radius=12)

            show_emote(MultiGame.screen,
                       PYGAME_EMOTES[mess["emote_index"]],
                       emote_container.x + 10,
                       emote_container.y + 10,
                       emote_size)

            y -= 5

        # write pseudo
        if mess["type"] == "emote" or (
                mess["type"] == "guess" and not mess["succeed"]):
            y -= 20
            image_texte = MEDIUM_FONT.render(mess["pseudo"], 1, (80, 80, 80))
            MultiGame.screen.blit(image_texte, (0.82 * MultiGame.W + 30, y))

        y -= 10

     # emotes
    emotes = [PYGAME_EMOTES[e] for e in PLAYER_DATA["purchased_items"]
              if SHOP_ITEMS[e]["category"] == "Emotes"]

    if len(emotes) > 0 and MultiGame.is_connected:
        emote_icon = pygame.image.load("assets/emote_icon.png").convert_alpha()
        emote_icon = pygame.transform.scale(emote_icon, (30, 30))
        MultiGame.screen.blit(emote_icon, (input_box.x + 5, input_box.y - 35))

        num_emotes_rows = int(math.sqrt(len(emotes)))
        num_emotes_column = math.ceil(len(emotes) / num_emotes_rows)

        emote_margin = 12
        emote_size = 50

        emotes_rect_size = (num_emotes_column * (emote_size + emote_margin),
                            num_emotes_rows * (emote_size + emote_margin))

        emotes_rect = pygame.Rect(
            input_box.x - emotes_rect_size[0] // 2,
            input_box.y - 45 - (
                emote_size + emote_margin) * num_emotes_rows,
            emotes_rect_size[0],
            emotes_rect_size[1])

        if MultiGame.show_emotes:
            pygame.draw.rect(
                MultiGame.screen,
                BEIGE,
                emotes_rect,
                border_radius=15)
            pygame.draw.rect(
                MultiGame.screen,
                BLACK,
                emotes_rect,
                1,
                border_radius=15)

            for i, emote in enumerate(emotes):
                x = emotes_rect.x + emote_margin + i % num_emotes_column * \
                    (emote_size + emote_margin) - emote_margin // 2
                y = emotes_rect.y + emote_margin + i // num_emotes_column * \
                    (emote_size + emote_margin) - emote_margin // 2

                show_emote(MultiGame.screen, emote, x, y, emote_size)

                for event in MultiGame.events:
                    if pygame.MOUSEBUTTONDOWN == event.type:
                        if pygame.Rect(
                                x, y, emote_size, emote_size).collidepoint(
                                pygame.mouse.get_pos()):
                            e_mess = {"header": "new_message",
                                      "type": "emote",
                                      "pid": MultiGame.PLAYER_ID,
                                      "pseudo": MultiGame.me["pseudo"],
                                      "emote_path": emote["image_path"].split("/")[-1],
                                      "emote_index": emote["index"]}
                            tools.send_ws(MultiGame.WS, e_mess)
                            MultiGame.MESSAGES.append(e_mess)

    for event in MultiGame.events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            MultiGame.guess_input_active = input_box.collidepoint(event.pos)
            if input_box.x + 5 <= event.pos[0] <= input_box.x + \
                    40 and input_box.y - 40 <= event.pos[1] <= input_box.y - 5:
                MultiGame.show_emotes = not MultiGame.show_emotes
            else:
                MultiGame.show_emotes = False

        if event.type == pygame.KEYDOWN and MultiGame.guess_input_active:
            if event.key == pygame.K_RETURN and MultiGame.guess.strip():
                tools.send_ws(MultiGame.WS,
                              {"header": "new_message",
                               "type": "guess",
                               "pid": MultiGame.PLAYER_ID,
                               "pseudo": MultiGame.me["pseudo"],
                               "message": MultiGame.guess,
                               "remaining_time": MultiGame.game_remaining_time})  # send message
                MultiGame.MESSAGES.append({"type": "guess",
                                           "pid": MultiGame.PLAYER_ID,
                                           "pseudo": MultiGame.me["pseudo"],
                                           "message": MultiGame.guess,
                                           "succeed": False})
                MultiGame.guess = ""
            elif event.key == pygame.K_BACKSPACE:
                MultiGame.guess = MultiGame.guess[:-1]
            else:
                MultiGame.guess += event.unicode
