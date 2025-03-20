import threading
import pygame
try:
    from pygame_emojis import load_emoji
except BaseException:
    import pygame.freetype
import sys
import tools
import MultiGame
import yaml
import tools
import asyncio
import json
from dotenv import load_dotenv
import os
import socketio
import json
from datetime import datetime, timedelta
import time

with open("assets/config.yaml", "r") as f:
    config = yaml.safe_load(f)

with open("assets/players_data.json") as f:
    player_data = json.load(f)

load_dotenv()
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")

# *pygame
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
BLEU_CLAIR = pygame.Color('lightskyblue3')
BLEU = pygame.Color('dodgerblue2')
BEIGE = (250, 240, 230)
VERT = (0, 255, 0)
ROUGE = (255, 0, 0)
JAUNE = (255, 255, 0)
MAGENTA = (255, 0, 255)
CYAN = (0, 255, 255)


class MultiplayersGame:
    def start_connexion(self):
        try:

            if not asyncio.run(tools.test_server()):  # start the serv

                import MultiGame.server as server
                self.server = server

                self.server_thread = threading.Thread(
                    target=server.start_server, daemon=True)
                self.server_thread.start()

                while not server.server_running:
                    time.sleep(0.1)

            asyncio.set_event_loop(self.connection_loop)
            self.connection_loop.run_until_complete(
                self.handle_connection_client())
        except RuntimeError:
            print("connexion fermé")

    async def handle_connection_client(self):
        self.sio = socketio.AsyncClient(logger=True, engineio_logger=True)

        @self.sio.event
        async def connect():  # joining the game
            await self.sio.emit("join", {"type": "join", "pseudo": player_data["pseudo"], "avatar": {"type": "matrix", "matrix": tools.load_bmp_to_matrix("assets/avatar.bmp")}})

        @self.sio.event
        async def disconnect():
            print("Déconnecté du serveur WebSocket.")

        @self.sio.on('welcome')
        async def welcome(data):
            self.connected = True
            MultiGame.ALL_FRAMES += data["all_frames"]
            MultiGame.PLAYER_ID = data["id"]
            MultiGame.MESSAGES = data["messages"]
            MultiGame.PLAYERS = data["players"]
            MultiGame.CURRENT_SENTENCE = data["sentence"]
            MultiGame.CURRENT_DRAWER = data["drawer_id"]
            tools.update_canva_by_frames(data["all_frames"], delay=False)

        @self.sio.on("new_player")
        async def new_player(data):
            MultiGame.PLAYERS.append(data)
            MultiGame.MESSAGES.append({"type": "system",
                                       "message": data["pseudo"] + " viens de nous rejoindre!",
                                       "color": config["succeed_color"]})

        @self.sio.on("player_disconnected")
        async def player_disconnected(data):
            for i in range(len(MultiGame.PLAYERS)):
                if MultiGame.PLAYERS[i]["id"] == data["pid"]:
                    player = MultiGame.PLAYERS.pop(i)
                    break

            MultiGame.MESSAGES.append({"type": "system",
                                       "message": player["pseudo"] + " à quitté la partie.",
                                       "color": config["bad_color"]})

        @self.sio.on("new_game")
        def new_game(data):
            # save draw
            if MultiGame.PLAYER_ID == MultiGame.CURRENT_DRAWER and MultiGame.CANVAS and MultiGame.CANVAS != [
                    [None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]:  # save your draw
                tools.save_canvas(
                    MultiGame.CANVAS,
                    f"assets/your_best_draws/{
                        datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.bmp",
                    MultiGame.CURRENT_SENTENCE)

            MultiGame.CANVAS = [[None for _ in range(config["canvas_width"])] for _ in range(
                config["canvas_height"])]  # reset canvas
            MultiGame.CURRENT_SENTENCE = data["new_sentence"]
            MultiGame.CURRENT_DRAWER = data["drawer_id"]
            MultiGame.MESSAGES = [{"type": "system", "message": "Nouvelle partie ! C'est le tour de " + [p["pseudo"]
                                                                                                         for p in MultiGame.PLAYERS if p["id"] == MultiGame.CURRENT_DRAWER][0], "color": config["succeed_color"]}]
            MultiGame.ALL_FRAMES = []
            MultiGame.FOUND = False
            MultiGame.GAMESTART = datetime.fromisoformat(data["start_time"])
            MultiGame.ROLL_BACK = 0

        @self.sio.on("draw")
        async def draw(frames):
            if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER:  # not the drawer
                MultiGame.ALL_FRAMES = tools.split_steps_by_roll_back(
                    MultiGame.ALL_FRAMES, MultiGame.ROLL_BACK)[0]
                MultiGame.ROLL_BACK = 0

                threading.Thread(
                    target=tools.update_canva_by_frames, kwargs={
                        "frames": frames}).start()  # update canvas in realtime

                num_steps = 0
                for frame in MultiGame.ALL_FRAMES:
                    if frame["type"] == "new_step":
                        num_steps += 1
                MultiGame.STEP_NUM = num_steps

        @self.sio.on("new_message")
        def new_message(guess):
            # ajouter à la liste de message
            if guess["pid"] == MultiGame.PLAYER_ID:
                MultiGame.MESSAGES = MultiGame.MESSAGES[:-1]
            MultiGame.MESSAGES.append(guess)

            # update found and points
            if guess["succeed"]:
                for i in range(len(MultiGame.PLAYERS)):
                    if MultiGame.PLAYERS[i]["id"] == guess["pid"]:
                        MultiGame.PLAYERS[i]["found"] = True

                for e in guess["new_points"]:
                    for i in range(len(MultiGame.PLAYERS)):
                        if MultiGame.PLAYERS[i]["id"] == e["pid"]:
                            MultiGame.PLAYERS[i]["points"] += e["points"]

        @self.sio.on("roll_back")
        async def roll_back(roll_back):
            if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER:
                MultiGame.ROLL_BACK = roll_back
                tools.update_canva_by_frames(
                    MultiGame.ALL_FRAMES, reset=True, delay=False)

        try:
            await self.sio.connect(f"https://{NGROK_DOMAIN}")

            # Boucle pour écouter et réagir aux messages
            await self.sio.wait()
        except asyncio.CancelledError:
            print("déconnecté du server")

    def timer(self):

        if len(MultiGame.PLAYERS) == 1:
            return

        timer_text = f"{
            self.game_remaining_time //
            60}:{
            0 if self.game_remaining_time %
            60 < 10 else ''}{
            self.game_remaining_time %
            60}"

        # Créer un texte pour le timer
        font = pygame.font.Font("assets/PermanentMarker.ttf", 25)
        text_surface = font.render(timer_text, True, (0, 0, 0))

        # Calculer la taille du rectangle (qui sera juste la taille du texte)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.W // 2, 25)  # Centré en haut de l'écran

        # Dessiner le rectangle autour du texte
        rect_x = text_rect.x - 10  # Un petit padding
        rect_y = text_rect.y - 5
        rect_width = text_rect.width + 20  # Un petit padding à droite et à gauche
        rect_height = text_rect.height + 5  # Un padding en haut et en bas
        pygame.draw.rect(self.screen, (230, 0, 0),
                         (rect_x, rect_y, rect_width, rect_height))

        # Afficher le texte du timer
        self.screen.blit(text_surface, text_rect)

    def players(self):
        pygame.draw.rect(
            self.screen,
            BLANC,
            (0.01 * self.W,
             0.04 * self.H,
             0.18 * self.W,
             0.7 * self.H))
        pygame.draw.rect(
            self.screen,
            NOIR,
            (0.01 * self.W,
             0.04 * self.H,
             0.18 * self.W,
             0.7 * self.H),
            1)

        font = pygame.font.Font("assets/PermanentMarker.ttf", 20)
        image_texte = font.render("Liste de joueurs:", 1, (0, 0, 0))
        self.screen.blit(image_texte, (5.5 / 100 * self.W, 6 / 100 * self.H))

        dico_co = [
            [(1 / 100 * self.W, (11 + i * 7) / 100 * self.H, 18 / 100 * self.W, 7 / 100 * self.H),
             (1.5 / 100 * self.W, (12 + i * 7) / 100 * self.H),
             (6 / 100 * self.W, (12.5 + i * 7) / 100 * self.H),
             (13 / 100 * self.W, (14 + i * 7) / 100 * self.H),
             (12 / 100 * self.W, (12 + i * 7) / 100 * self.H),
             (17.4 / 100 * self.W, (13.2 + i * 7) / 100 * self.H)]
            for i in range(9)  # Génère 9 entrées automatiquement
        ]

        for y, player in enumerate(MultiGame.PLAYERS):

            # fond
            pygame.draw.rect(
                self.screen,
                (222,
                 0,
                 0) if player["id"] == MultiGame.CURRENT_DRAWER else (
                    0,
                    0,
                    0),
                dico_co[y][0])
            pygame.draw.rect(self.screen,
                             config["players_colors"][y % len(config["players_colors"])],
                             (dico_co[y][0][0] + 3,
                              dico_co[y][0][1] + 3,
                                 dico_co[y][0][2] - 6,
                                 dico_co[y][0][3] - 6))

            # avatar TODO FOR EMOJI!!!!
            if player["avatar"]["type"] == "matrix":
                avatar = tools.matrix_to_image(player["avatar"]["matrix"])
                avatar = pygame.transform.scale(
                    avatar, (5 / 100 * self.H, 5 / 100 * self.H))
                pygame.draw.circle(
                    self.screen,
                    BLEU,
                    (dico_co[y][1][0] +
                     avatar.get_width() //
                     2,
                     dico_co[y][1][1] +
                        avatar.get_height() //
                        2),
                    avatar.get_width() //
                    2 +
                    3)
                tools.apply_circular_mask(avatar)
                self.screen.blit(avatar, dico_co[y][1])
            else:  # emoji

                pygame.draw.circle(
                    self.screen,
                    BLEU,
                    (dico_co[y][1][0] +
                     5 /
                     100 *
                     self.H //
                     2,
                     dico_co[y][1][1] +
                        5 /
                        100 *
                        self.H //
                        2),
                    5 /
                    100 *
                    self.H //
                    2 +
                    3)
                pygame.draw.circle(
                    self.screen,
                    player["avatar"]["color"],
                    (dico_co[y][1][0] + 5 / 100 * self.H // 2,
                     dico_co[y][1][1] + 5 / 100 * self.H // 2),
                    5 / 100 * self.H // 2)

                try:
                    self.screen.blit(
                        load_emoji(
                            player["avatar"]["emoji"],
                            (4.6 / 100 * self.H,
                             4.6 / 100 * self.H)),
                        (dico_co[y][1][0],
                         dico_co[y][1][1] + 4))
                    self.screen.blit(
                        load_emoji(
                            player["avatar"]["emoji"],
                            (4.6 / 100 * self.H,
                             4.6 / 100 * self.H)),
                        (dico_co[y][1][0],
                         dico_co[y][1][1] + 4))
                except BaseException:
                    seguisy80 = pygame.freetype.SysFont("segoeuisymbol", 30)
                    emoji, rect = seguisy80.render(
                        player["avatar"]["emoji"], "black")
                    rect.center = (
                        dico_co[y][1][0] + 20,
                        dico_co[y][1][1] + 24)
                    self.screen.blit(emoji, rect)

            # pseudo
            text_color = (
                10,
                10,
                10) if player["id"] == MultiGame.PLAYER_ID else (
                100,
                100,
                100)
            font = pygame.font.Font("assets/PermanentMarker.ttf", 30)
            image_texte = font.render(player["pseudo"], 1, text_color)
            self.screen.blit(image_texte, dico_co[y][2])
            # points
            font = pygame.font.Font("assets/PermanentMarker.ttf", 20)
            image_texte = font.render(
                "points:  " + str(player["points"]), 1, text_color)
            self.screen.blit(image_texte, dico_co[y][3])

            if player["id"] != MultiGame.CURRENT_DRAWER:
                image_texte = font.render("Trouvé ", 1, text_color)
                self.screen.blit(image_texte, dico_co[y][4])

                # pygame.draw.circle(self.screen, text_color, dico_co[y][4], 7)
                if player["found"]:
                    pygame.draw.circle(self.screen, VERT, dico_co[y][5], 5)
                else:
                    pygame.draw.circle(self.screen, ROUGE, dico_co[y][5], 5)

    def sentence(self):
        pygame.draw.rect(
            self.screen,
            BLANC,
            (0.01 * self.W,
             0.75 * self.H,
             0.18 * self.W,
             0.2 * self.H))
        pygame.draw.rect(
            self.screen,
            NOIR,
            (0.01 * self.W,
             0.75 * self.H,
             0.18 * self.W,
             0.2 * self.H),
            1)

        text = "Phrase à faire deviner:"if self.me["is_drawer"] else "Phrase à trouver:"
        pygame.draw.rect(
            self.screen,
            VERT,
            (1 / 100 * self.W,
             75 / 100 * self.H,
             18 / 100 * self.W,
             20 / 100 * self.H))

        font = pygame.font.Font("assets/PermanentMarker.ttf", 22)
        image_texte = font.render(text, True, (0, 0, 0))
        self.screen.blit(image_texte, (2 / 100 * self.W, 77 / 100 * self.H))

        if len(MultiGame.CURRENT_SENTENCE) > 0:
            FONT_SIZE_BASE = 20  # Taille de base de la font
            Y_START = 77 / 100 * self.H + 36  # Position de départ

            # Choisir la taille de font en fonction de la longueur du texte
            if len(MultiGame.CURRENT_SENTENCE) <= 30:
                font_size = FONT_SIZE_BASE
            elif len(MultiGame.CURRENT_SENTENCE) <= 60:
                font_size = FONT_SIZE_BASE - 2
            else:
                font_size = FONT_SIZE_BASE - 4

            font = pygame.font.Font("assets/PermanentMarker.ttf", font_size)

            lines = tools.lines_return(
                MultiGame.CURRENT_SENTENCE, font, 0.16 * self.W)

            # Affichage ligne par ligne
            for i, ligne in enumerate(lines):
                image_texte = font.render(ligne, True, (20, 10, 10))
                if (not self.me["found"]) and not self.me["is_drawer"]:
                    image_texte = tools.flou(image_texte)
                self.screen.blit(image_texte, (0.03 * self.W,
                                 Y_START + (i * (font_size + 2))))

    def drawing(self):
        """Permet de dessiner uniquement dans la zone de dessin."""
        if not MultiGame.CANVAS:
            return

        zone_x_min = int(0.2 * self.W) + 2    # 20% de la largeur de la fenêtre
        zone_x_max = int(0.8 * self.W) - 4    # 60% de la largeur de la fenêtre
        zone_y_min = int(0.04 * self.H) + 2   # Commence en haut de la fenêtre
        # Remplie toute la hauteur de la fenêtre
        zone_y_max = int(0.96 * self.H) - 4

        canvas_width = len(MultiGame.CANVAS[0])
        canvas_height = len(MultiGame.CANVAS)

        # Affichage du CANVAS à l'écran
        self.pixel_width = (zone_x_max - zone_x_min) // canvas_width
        self.pixel_height = (zone_y_max - zone_y_min) // canvas_height

        zone_x_min = self.W // 2 - self.pixel_width * canvas_width // 2
        zone_x_max = self.W // 2 + self.pixel_width * canvas_width // 2
        zone_y_min = self.H // 2 - self.pixel_height * canvas_height // 2
        zone_y_max = self.H // 2 + self.pixel_height * canvas_height // 2

        pygame.draw.rect(
            self.screen,
            NOIR,
            (zone_x_min -
             1,
             zone_y_min -
             1,
             zone_x_max -
             zone_x_min +
             2,
             zone_y_max -
             zone_y_min +
             2),
            1)

        #! show
        for y in range(canvas_height):
            for x in range(canvas_width):
                color = MultiGame.CANVAS[y][x] if MultiGame.CANVAS[y][x] else BLANC
                pygame.draw.rect(
                    self.screen,
                    color,
                    (zone_x_min +
                     x *
                     self.pixel_width,
                     zone_y_min +
                     y *
                     self.pixel_height,
                     self.pixel_width,
                     self.pixel_height))

        #! drawing
        if self.me["is_drawer"]:
            # Vérifier si le clic est dans la zone de dessin
            if zone_x_min <= self.mouse_pos[0] <= zone_x_max and zone_y_min <= self.mouse_pos[1] <= zone_y_max:
                for event in self.events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        MultiGame.ALL_FRAMES = tools.split_steps_by_roll_back(
                            MultiGame.ALL_FRAMES, MultiGame.ROLL_BACK)[0]
                        MultiGame.STEP_NUM = 0
                        for frame in MultiGame.ALL_FRAMES:
                            if frame["type"] in ["new_step", "shape"]:
                                MultiGame.STEP_NUM += 1

                        MultiGame.ROLL_BACK = 0
                        self.second_draw_frames.append({"type": "new_step"})
                        MultiGame.ALL_FRAMES.append({"type": "new_step"})

                    elif self.mouseDown and event.type == pygame.MOUSEMOTION:
                        # can draw
                        if self.lastMouseDown and 0 < self.game_remaining_time < config[
                                "game_duration"]:
                            # Position actuelle dans le CANVAS
                            canvas_x = (
                                event.pos[0] - zone_x_min) // self.pixel_width
                            canvas_y = (
                                event.pos[1] - zone_y_min) // self.pixel_height

                            # Dessiner une ligne entre last_click et la
                            # position actuelle
                            if self.last_canvas_click and self.last_canvas_click != (
                                    canvas_x, canvas_y):
                                x1, y1 = self.last_canvas_click
                                x2, y2 = canvas_x, canvas_y

                                # Générer les points entre les deux
                                MultiGame.CANVAS = tools.draw_brush_line(
                                    MultiGame.CANVAS, x1, y1, x2, y2, self.pen_color, self.pen_radius, 0)
                                self.second_draw_frames.append(
                                    {
                                        "type": "line",
                                        "x1": x1,
                                        "y1": y1,
                                        "x2": x2,
                                        "y2": y2,
                                        "color": self.pen_color,
                                        "radius": self.pen_radius})
                                MultiGame.ALL_FRAMES.append(
                                    {
                                        "type": "type",
                                        "x1": x1,
                                        "y1": y1,
                                        "x2": x2,
                                        "y2": y2,
                                        "color": self.pen_color,
                                        "radius": self.pen_radius})

                            # Mettre à jour la dernière position
                            self.last_canvas_click = (canvas_x, canvas_y)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        MultiGame.STEP_NUM += 1

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_z and (
                                pygame.key.get_mods() & pygame.KMOD_CTRL):  # CTRL+Z

                            MultiGame.ROLL_BACK = min(
                                MultiGame.STEP_NUM, MultiGame.ROLL_BACK + 1)

                            tools.update_canva_by_frames(
                                MultiGame.ALL_FRAMES, delay=False, reset=True)

                            tools.emit_sio(
                                self.sio, "roll_back", MultiGame.ROLL_BACK)

                        # CTRL+Y
                        elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):

                            MultiGame.ROLL_BACK = max(
                                0, MultiGame.ROLL_BACK - 1)

                            tools.update_canva_by_frames(
                                MultiGame.ALL_FRAMES, delay=False, reset=True)

                            tools.emit_sio(
                                self.sio, "roll_back", MultiGame.ROLL_BACK)

        # send draw
        if self.frame_num == config["game_page_fps"] - \
                1 and self.second_draw_frames != []:
            print("draw sended")
            tools.emit_sio(
                self.sio, "draw", tools.simplify_frames(
                    self.second_draw_frames))  # send draw
            self.second_draw_frames = []

    def couleurs(self):
        pygame.draw.rect(
            self.screen,
            BLANC,
            (0.81 * self.W,
             0.04 * self.H,
             0.18 * self.W,
             0.25 * self.H))
        pygame.draw.rect(
            self.screen,
            NOIR,
            (0.81 * self.W,
             0.04 * self.H,
             0.18 * self.W,
             0.25 * self.H),
            1)

        """Affiche une palette de couleurs fixes et permet de sélectionner une couleur."""
        palette_x, palette_y = int(0.81 * self.W), int(0.04 * self.H)
        palette_w, palette_h = int(0.18 * self.W), int(0.25 * self.H)

        # Taille des carrés de couleur
        cols = 4  # Nombre de couleurs par ligne
        square_size = min(palette_w // cols, palette_h //
                          (len(config["drawing_colors"]) // cols + 1))
        spacing = 10  # Espacement entre les couleurs
        offset_x = (palette_w - (square_size + spacing)
                    * cols) // 2  # Centrage horizontal

        for i, color in enumerate(config["drawing_colors"]):
            row = i // cols
            col = i % cols
            x = palette_x + col * (square_size + spacing) + offset_x + 5
            y = palette_y + row * (square_size + spacing)
            pygame.draw.rect(
                self.screen, color, (x, y, square_size, square_size))
            pygame.draw.rect(
                self.screen, (0, 0, 0), (x, y, square_size, square_size), 2)  # Bordure noire

        # Afficher la couleur sélectionnée
        selected_x = palette_x + palette_w // 2 - 50
        selected_y = palette_y + palette_h - 25
        pygame.draw.rect(self.screen, self.pen_color,
                         (selected_x, selected_y, 100, 30))
        pygame.draw.rect(self.screen, (0, 0, 0), (selected_x,
                         selected_y, 100, 30), 2)  # Bordure noire

        # Gestion du clic sur une couleur
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for i, color in enumerate(config["drawing_colors"]):
                    row = i // cols
                    col = i % cols
                    x = palette_x + col * (square_size + spacing) + offset_x
                    y = palette_y + row * (square_size + spacing)

                    if x <= mouse_x < x + square_size and y <= mouse_y < y + square_size:
                        self.pen_color = color
                        break  # Empêche de changer plusieurs fois la couleur dans une seule itération

    def slider_radius(self):
        pygame.draw.rect(
            self.screen,
            BLANC,
            (0.81 * self.W,
             0.3083 * self.H,
             0.18 * self.W,
             0.0833 * self.H))
        pygame.draw.rect(
            self.screen,
            NOIR,
            (0.81 * self.W,
             0.3083 * self.H,
             0.18 * self.W,
             0.0833 * self.H),
            1)

        try:
            self.pixel_height  # test la variable
        except BaseException:
            return

        slider_x, slider_y, slider_w, slider_h = (
            0.81 * self.W, 0.3083 * self.H, 0.18 * self.W, 0.0833 * self.H
        )
        slider_min = slider_x + 10
        slider_max = slider_x + slider_w - 10
        radius_slider_pos = slider_min + \
            (self.pen_radius // self.pixel_height - 1) * (slider_max - slider_min) / 10

        # Fond du slider
        pygame.draw.rect(self.screen, (200, 200, 200),
                         (slider_x, slider_y, slider_w, slider_h))

        # Barre de progression
        pygame.draw.line(
            self.screen,
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
        pygame.draw.circle(self.screen, (255, 180, 50), (int(
            radius_slider_pos), slider_y + slider_h // 2 + 1), self.pen_radius)

        # Cercle de prévisualisation (taille du crayon)
        # pygame.draw.circle(self.screen, self.pen_color, (int(slider_x) - 20, int(slider_y + slider_h // 2)), self.pen_radius)

        # update
        for event in self.events:
            if event.type == pygame.MOUSEMOTION and self.mouseDown:
                if slider_min - self.pen_radius <= event.pos[0] <= slider_max + \
                        self.pen_radius and slider_y <= event.pos[1] <= slider_y + slider_h:
                    radius_slider_pos = max(
                        slider_min, min(
                            event.pos[0], slider_max))
                    self.pen_radius = int((int(1 +
                                               (radius_slider_pos -
                                                slider_min) *
                                               10 /
                                               (slider_max -
                                                slider_min))) *
                                          self.pixel_height)

    def chat(self):

        font = pygame.font.Font("assets/PermanentMarker.ttf", 18)
        guess_line = tools.lines_return(self.guess, font, 0.15 * self.W)
        input_box = pygame.Rect(0.82 *
                                self.W, 0.9533 *
                                self.H -
                                45 -
                                len(guess_line) *
                                20, 0.16 *
                                self.W, max(40, 15 +
                                            20 *
                                            len(guess_line)))

        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.guess_input_active = input_box.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and self.guess_input_active:
                if event.key == pygame.K_RETURN and self.guess.strip():
                    tools.emit_sio(self.sio,
                                   "guess",
                                   {"pid": MultiGame.PLAYER_ID,
                                    "pseudo": self.me["pseudo"],
                                       "message": self.guess,
                                       "remaining_time": self.game_remaining_time})  # send message
                    MultiGame.MESSAGES.append(
                        {"type": "guess", "pseudo": self.me["pseudo"], "message": self.guess, "succeed": False})
                    self.guess = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.guess = self.guess[:-1]
                else:
                    self.guess += event.unicode

        # Mise à jour visuelle
        min_y = 0.4083 * \
            self.H if self.me["is_drawer"] else 0.04 * self.H - 45 - len(guess_line) * 20
        pygame.draw.rect(
            self.screen,
            BLANC,
            (0.81 *
             self.W,
             min_y,
             0.18 *
             self.W,
             0.9533 *
             self.H -
             min_y))
        pygame.draw.rect(
            self.screen,
            NOIR,
            (0.81 *
             self.W,
             min_y,
             0.18 *
             self.W,
             0.9533 *
             self.H -
             min_y),
            1)

        color = BLEU if self.guess_input_active else BLEU_CLAIR
        for i, line in enumerate(guess_line):
            txt_surface = font.render(line, True, NOIR)
            self.screen.blit(
                txt_surface, (input_box.x + 5, input_box.y + 5 + i * 20))
        pygame.draw.rect(self.screen, color, input_box, 2)

        # chat
        y = 0.9533 * self.H - 60 - len(guess_line) * 20

        for mess in MultiGame.MESSAGES[::-1]:
            font = pygame.font.Font("assets/PermanentMarker.ttf", 16)
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
            lines = tools.lines_return(text, font, 0.16 * self.W)

            for line in lines[::-1]:
                if y > min_y + 16:
                    y -= 19

                    image_texte = font.render(line, 1, color)
                    self.screen.blit(image_texte, (0.82 * self.W, y))

            if y < min_y + 18:
                break

            # write pseudo
            if mess["type"] == "guess" and not mess["succeed"]:
                y -= 20
                image_texte = font.render(mess["pseudo"], 1, (80, 80, 80))
                self.screen.blit(image_texte, (0.82 * self.W + 30, y))

            y -= 10

    def disconnect(self):
        self.sio.disconnect()
        for task in asyncio.all_tasks(self.connection_loop):
            task.cancel()
        self.connection_loop.stop()
        if self.server:
            self.server.stop_server()
        self.connexion_thread.join()
        print("deco")

    def __init__(self, screen, clock, W, H):
        if not tools.is_connected():
            print("Désolé, une connexion internet est requise.")
            return

        self.screen, self.W, self.H = screen, W, H
        self.connected = False
        self.server = None

        try:
            self.connection_loop = asyncio.new_event_loop()
            self.connexion_thread = threading.Thread(
                target=self.start_connexion)
            self.connexion_thread.start()

            self.game_remaining_time = config["game_duration"]

            self.me = {"id": -1,
                       "pseudo": "",
                       "points": 0,
                       "found": False,
                       "is_drawer": False
                       }

            # pen values
            self.pen_color = (0, 0, 0)
            self.pen_radius = 6
            self.mouseDown = False
            self.lastMouseDown = False
            self.last_canvas_click = None

            self.mouse_pos = (0, 0)

            # for drawing
            self.second_draw_frames = []

            self.frame_num = 0

            self.guess_input_active = False
            self.guess = ""

            MultiGame.PLAYERS = []

            while 1:
                clock.tick(config["game_page_fps"])

                for player in MultiGame.PLAYERS:
                    if player["id"] == MultiGame.PLAYER_ID:
                        self.me = player
                        self.me["is_drawer"] = MultiGame.PLAYER_ID == MultiGame.CURRENT_DRAWER
                        break

                if self.frame_num % 2 == 0:
                    self.game_remaining_time = max(
                        0,
                        (MultiGame.GAMESTART +
                         timedelta(
                             seconds=config["game_duration"]) -
                            datetime.now()).seconds %
                        config["game_duration"] if MultiGame.GAMESTART else config["game_duration"])

                    if self.game_remaining_time == 0:  # if game time over
                        if self.me["is_drawer"]:
                            tools.emit_sio(self.sio, "game_finished", None)
                        MultiGame.GAMESTART = datetime.now()

                self.events = pygame.event.get()

                self.screen.fill(BEIGE)

                self.players()
                self.sentence()
                self.drawing()
                self.chat()
                if self.me["id"] == MultiGame.PLAYER_ID:
                    self.couleurs()
                    self.slider_radius()
                self.timer()

                if not self.connected:
                    font = pygame.font.Font("assets/PermanentMarker.ttf", 20)
                    text = font.render(
                        "Connexion au serveur...", True, (0, 0, 0))
                    self.screen.blit(
                        text,
                        text.get_rect(
                            center=(
                                self.W //
                                2 +
                                5,
                                self.H //
                                2 -
                                100)))

                for event in self.events:
                    if (event.type == pygame.KEYDOWN and event.key ==
                            pygame.K_q and not self.guess_input_active) or event.type == pygame.QUIT:
                        threading.Thread(
                            target=self.disconnect, daemon=True).start()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.mouseDown = True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.mouseDown = False
                        self.last_canvas_click = None
                    if event.type == pygame.MOUSEMOTION:
                        self.mouse_pos = event.pos
                        if self.mouseDown:
                            self.lastMouseDown = self.mouseDown
                    if event.type == pygame.VIDEORESIZE:
                        self.W, self.H = tools.get_screen_size()

                pygame.display.flip()

                self.frame_num = (self.frame_num + 1) % config["game_page_fps"]

        except KeyboardInterrupt:
            self.disconnect()
            os._exit(0)
