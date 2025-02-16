import pygame
import sys
import tools
import gameVar
import yaml
import tools
import asyncio
import json

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

#*pygame
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
BLEU_CLAIR = pygame.Color('lightskyblue3')
BLEU = pygame.Color('dodgerblue2')
BEIGE = (250, 240, 230)
VERT = (0,255,0)
ROUGE= (255,0,0)
JAUNE=(255,255,0)
MAGENTA=(255,0,255)
CYAN=(0,255,255)

def input_pseudo():
    """Affiche une fenêtre pour entrer le pseudo"""
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Entrez votre pseudo")
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(100, 80, 200, 40)
    text = ''
    active = True
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(BLANC)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and text.strip():
                    pygame.quit()
                    return text  # Retourne le pseudo saisi
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        # Mise à jour visuelle
        color = BLEU if active else BLEU_CLAIR
        txt_surface = font.render(text, True, NOIR)
        input_box.w = max(200, txt_surface.get_width() + 10)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)



class gamePage:
    
    def background(self):
        self.screen.fill(BEIGE)
        pygame.draw.rect(self.screen, BLANC,(20/100*self.W, 4/100*self.H, 60/100*self.W, 91/100*self.H) )
        pygame.draw.rect(self.screen, BLANC,(1/100*self.W, 4/100*self.H, 18/100*self.W, 70/100*self.H) )
        pygame.draw.rect(self.screen, BLANC,(81/100*self.W, 4/100*self.H, 18/100*self.W, 25/100*self.H) )
        pygame.draw.rect(self.screen, BLANC,(81/100*self.W, 30.83/100*self.H, 18/100*self.W, 8.33/100*self.H) )
        pygame.draw.rect(self.screen, BLANC,(81/100*self.W, 40.83/100*self.H, 18/100*self.W, 54.5/100*self.H) )
        
        self.zones = [
            (0.2 * self.W, 0.04 * self.H, 0.6 * self.W, 0.91 * self.H),  # Zone de dessin
            (0.01 * self.W, 0.04 * self.H, 0.18 * self.W, 0.7 * self.H),  # Liste personnes
            (0.01 * self.W, 0.75 * self.H, 0.18 * self.W, 0.2 * self.H),  # Mot à deviner
            (0.81 * self.W, 0.04 * self.H, 0.18 * self.W, 0.25 * self.H),  # Couleurs
            (0.81 * self.W, 0.3083 * self.H, 0.18 * self.W, 0.0833 * self.H),  # Style de stylo
            (0.81 * self.W, 0.4083 * self.H, 0.18 * self.W, 0.545 * self.H),  # Chat
            (0.01 * self.W, 0.04 * self.H, 0.18 * self.W, 0.07 * self.H),  # Texte joueurs
        ]
        
        for x, y, w, h in self.zones:
            pygame.draw.rect(self.screen, NOIR, (x, y, w, h), 1)
            
    def timer(self):
        if self.frame_num==config["game_page_fps"]-1 and len(gameVar.PLAYERS)>1:
            self.game_remaining_time=max(0,self.game_remaining_time-1)
            
        timer_text = f"{self.game_remaining_time//60}:{0 if self.game_remaining_time%60<10 else ''}{self.game_remaining_time%60}"
        
        # Créer un texte pour le timer
        font = pygame.font.Font("PermanentMarker.ttf", 25)
        text_surface = font.render(timer_text, True, (0,0,0))
        
        # Calculer la taille du rectangle (qui sera juste la taille du texte)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.W // 2, 25)  # Centré en haut de l'écran

        # Dessiner le rectangle autour du texte
        rect_x = text_rect.x - 10  # Un petit padding
        rect_y = text_rect.y - 5
        rect_width = text_rect.width + 20  # Un petit padding à droite et à gauche
        rect_height = text_rect.height + 5  # Un padding en haut et en bas
        pygame.draw.rect(self.screen, (230,0,0), (rect_x, rect_y, rect_width, rect_height))

        # Afficher le texte du timer
        self.screen.blit(text_surface, text_rect)
        
        
        if self.me["id"] == gameVar.CURRENT_DRAWER and self.game_remaining_time==0: #if game time over
            gameVar["WS"].send(json.dumps({"type":"game_finished"}))
            
        if self.me["id"] == gameVar.CURRENT_DRAWER:
            list_found=[]
            for player in gameVar.PLAYERS:
                list_found.append(player["found"])
            if all(list_found):
                gameVar.WS.send(json.dumps({"type":"game_finished"}))
            
        if self.game_remaining_time%10==0 and self.frame_num>=config["game_page_fps"]-1:# for keep connection
            gameVar.WS.ping()
    
    def players(self):
        font = pygame.font.Font("PermanentMarker.ttf" ,20)
        image_texte = font.render ( "Liste de joueurs:", 1 , (0,0,0) )
        self.screen.blit(image_texte, (5.5/100*self.W,6/100*self.H))


        dico_co = [
            [(4/100*self.W,(12.5+i*7)/100*self.H),
             (1/100*self.W, (11+i*7)/100*self.H, 18/100*self.W, 7/100*self.H),
             (12/100*self.W,(14+i*7)/100*self.H),
             (17.4/100*self.W,(13.2+i*7)/100*self.H),
             (12/100*self.W,(12+i*7)/100*self.H)]
            for i in range(9)  # Génère 9 entrées automatiquement
        ]
        
        # sort players by points
        playersList=gameVar.PLAYERS
        playersList.sort(key=lambda x: x["points"])

        for y,player in enumerate(playersList):
            text_color=(10,10,10) if player["id"] == gameVar.PLAYER_ID else (100,100,100)

            pygame.draw.rect(self.screen, (222,0,0) if player["id"]==gameVar.CURRENT_DRAWER else (0,0,0),dico_co[y][1])
            pygame.draw.rect(self.screen, config["players_colors"][y],(dico_co[y][1][0]+3,dico_co[y][1][1]+3,dico_co[y][1][2]-6,dico_co[y][1][3]-6))
            font = pygame.font.Font("PermanentMarker.ttf" ,30)
            image_texte = font.render ( player["pseudo"], 1 , text_color )
            font = pygame.font.Font("PermanentMarker.ttf" ,20)
            self.screen.blit(image_texte, dico_co[y][0])
            image_texte = font.render ( "points:    "+str(player["points"]), 1 , text_color )
            self.screen.blit(image_texte, dico_co[y][2])

            image_texte = font.render ( "Trouvé ", 1 , text_color )
            self.screen.blit(image_texte, dico_co[y][4])
            pygame.draw.circle(self.screen, text_color, dico_co[y][3], 7)
            if player["found"]:
                pygame.draw.circle(self.screen, VERT,dico_co[y][3], 5)
            else:
                pygame.draw.circle(self.screen, ROUGE,dico_co[y][3], 5)
    
    def sentence(self):
        pygame.draw.rect(self.screen, VERT,(1/100*self.W,75/100*self.H, 18/100*self.W, 20/100*self.H) )

        font = pygame.font.Font("PermanentMarker.ttf" ,20)
        image_texte = font.render ( "Mot à faire deviner:", 1 , (0,0,0) )
        self.screen.blit(image_texte, (4/100*self.W,77/100*self.H))
        
        if len(gameVar.CURRENT_SENTENCE) >0:
            MAX_LARGEUR = 20  # Nombre max de caractères par ligne (ajuste si besoin)
            FONT_SIZE_BASE = 22  # Taille de base de la font
            Y_START = 77 / 100 * self.H +36 # Position de départ

            # Choisir la taille de font en fonction de la longueur du texte
            if len(gameVar.CURRENT_SENTENCE) <= MAX_LARGEUR:
                font_size = FONT_SIZE_BASE
            elif len(gameVar.CURRENT_SENTENCE) <= 2 * MAX_LARGEUR:
                font_size = FONT_SIZE_BASE - 2
            else:
                font_size = FONT_SIZE_BASE - 4

            font = pygame.font.Font("PermanentMarker.ttf", font_size)

            # Découpage intelligent du texte (évite de couper en plein milieu des mots)
            mots = gameVar.CURRENT_SENTENCE.split()
            lignes = []
            ligne_actuelle = ""

            for mot in mots:
                if len(ligne_actuelle + " " + mot) <= MAX_LARGEUR:
                    ligne_actuelle += " " + mot if ligne_actuelle else mot
                else:
                    lignes.append(ligne_actuelle)
                    ligne_actuelle = mot
            if ligne_actuelle:
                lignes.append(ligne_actuelle)

            # Affichage ligne par ligne
            for i, ligne in enumerate(lignes):
                image_texte = font.render(ligne, True, (0, 0, 0))
                if not self.me["found"] or self.me["id"] != gameVar.CURRENT_DRAWER:
                    image_texte=tools.flou(image_texte)
                self.screen.blit(image_texte, (0.03 * self.W, Y_START + (i * (font_size + 2))))
                
    def drawing(self):
        """Permet de dessiner uniquement dans la zone de dessin."""
        if not gameVar.CANVAS:
            return
        
        
        zone_x_min = int(0.2 * self.W)+2    # 20% de la largeur de la fenêtre
        zone_x_max = int(0.8 * self.W)-4    # 60% de la largeur de la fenêtre
        zone_y_min = int(0.04 * self.H)+2   # Commence en haut de la fenêtre
        zone_y_max = int(0.96 * self.H)-4   # Remplie toute la hauteur de la fenêtre
        
        canvas_width = len(gameVar.CANVAS[0])
        canvas_height = len(gameVar.CANVAS)

        # Affichage du CANVAS à l'écran
        pixel_width = (zone_x_max - zone_x_min) // canvas_width
        pixel_height = (zone_y_max - zone_y_min) // canvas_height

        #! show
        for y in range(canvas_height):
            for x in range(canvas_width):
                color = gameVar.CANVAS[y][x] if gameVar.CANVAS[y][x] else BLANC
                pygame.draw.rect(self.screen, color, (zone_x_min + x * pixel_width, zone_y_min + y * pixel_height, pixel_width, pixel_height))

        #! drawing
        if self.me["id"] == gameVar.CURRENT_DRAWER and len(gameVar.PLAYERS)>1:
            for event in self.events:
                if self.mouseDown and event.type == pygame.MOUSEMOTION:
                    # Vérifier si le clic est dans la zone de dessin
                    if zone_x_min <= event.pos[0] <= zone_x_max and zone_y_min <= event.pos[1] <= zone_y_max:
                        if self.lastMouseDown:
                            # Position actuelle dans le CANVAS
                            canvas_x = (event.pos[0] - zone_x_min) // pixel_width
                            canvas_y = (event.pos[1] - zone_y_min) // pixel_height

                            # Dessiner une ligne entre last_click et la position actuelle
                            if self.last_canvas_click and self.last_canvas_click != (canvas_x, canvas_y):
                                x1, y1 = self.last_canvas_click
                                x2, y2 = canvas_x, canvas_y

                                # Générer les points entre les deux
                                gameVar.CANVAS = tools.draw_brush_line(gameVar.CANVAS, x1, y1, x2, y2, self.pen_color, self.pen_radius)
                                self.frames.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": self.pen_color, "radius": self.pen_radius})

                            # Mettre à jour la dernière position
                            self.last_canvas_click = (canvas_x, canvas_y)

            #send draw
            if self.frame_num>=config["game_page_fps"]-1:
                if self.frames!=[]:
                    asyncio.run(tools.websocket_draw(gameVar.CANVAS, self.frames))
                    self.frames=[]
        
    def couleurs(self):
        """Affiche une palette de couleurs fixes et permet de sélectionner une couleur."""
        palette_x, palette_y = int(0.81 * self.W), int(0.04 * self.H)+8
        palette_w, palette_h = int(0.18 * self.W), int(0.25 * self.H)

        # Taille des carrés de couleur
        cols = 4  # Nombre de couleurs par ligne
        square_size = min(palette_w // cols, palette_h // (len(config["drawing_colors"]) // cols + 1))
        spacing = 10  # Espacement entre les couleurs
        offset_x = (palette_w - (square_size + spacing) * cols) // 2  # Centrage horizontal

        for i, color in enumerate(config["drawing_colors"]):
            row = i // cols
            col = i % cols
            x = palette_x + col * (square_size + spacing) + offset_x
            y = palette_y + row * (square_size + spacing)
            pygame.draw.rect(self.screen, color, (x, y, square_size, square_size))
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, square_size, square_size), 2)  # Bordure noire

        # Afficher la couleur sélectionnée
        selected_x = palette_x + palette_w // 2 - 50
        selected_y = palette_y + palette_h - 25
        pygame.draw.rect(self.screen, self.pen_color, (selected_x, selected_y, 100, 30))
        pygame.draw.rect(self.screen, (0, 0, 0), (selected_x, selected_y, 100, 30), 2)  # Bordure noire

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


    def chat(self):
        (0.81 * self.W, 0.4083 * self.H, 0.18 * self.W, 0.545 * self.H),  # Chat
        
        for mess in gameVar.MESSAGES:
            font = pygame.font.Font("PermanentMarker.ttf" ,15)
            image_texte = font.render ( mess["pseudo"], 1 , (80,80,80) )
            self.screen.blit(image_texte, (0.82 * self.W + 30, 0.41 * self.H))
            font = pygame.font.Font("PermanentMarker.ttf" ,12)
            image_texte = font.render ( mess["guess"], 1 , (0,0,0) )
            self.screen.blit(image_texte, (0.82 * self.W, 0.41 * self.H + 20))
    
    def __init__(self):
        pygame.init()
        
        # Dimensions de la fenêtre
        self.W, self.H = tools.get_screen_size()
        self.screen = pygame.display.set_mode((self.W,self.H))
        pygame.display.set_caption("UIdrawer")
        self.clock = pygame.time.Clock()
        
        self.game_remaining_time=config["game_duration"]
        
        self.me={   "id": -1,
                    "pseudo": "",
                    "points": 0,
                    "found":False,}
        
        #pen values
        self.pen_color=(0,0,0)
        self.pen_radius=1
        self.mouseDown=False
        self.lastMouseDown=False
        self.last_canvas_click=None
        
        #for drawing
        self.frames=[]
        self.frame_num=0
        
        self.running = True
        while self.running:
            
            for player in gameVar.PLAYERS:
                if player["id"] == gameVar.PLAYER_ID:
                    self.me=player #my data
            
            self.events=pygame.event.get()
            
            #* widget
            self.background()
            self.players()
            self.sentence()
            self.drawing()
            self.chat()
            self.couleurs()
            #self.timer()
            
            #* events
            for event in self.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.QUIT:
                        self.running=False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouseDown=True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseDown=False
                    self.last_canvas_click=None
                if event.type == pygame.MOUSEMOTION and self.mouseDown:
                    self.lastMouseDown=self.mouseDown
                    
            
            #* game
            pygame.display.flip()
            
            self.frame_num=(self.frame_num+1)%config["game_page_fps"]
            self.clock.tick(config["game_page_fps"])