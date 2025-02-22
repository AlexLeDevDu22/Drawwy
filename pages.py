import pygame
import sys
import tools
import gameVar
import yaml
import tools
import asyncio
import json
import pygetwindow as gw
from datetime import datetime, timedelta

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
    pygame.init()
    pygame.display.set_icon(pygame.image.load("icon.png"))
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Entrez votre pseudo")
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(100, 80, 200, 40)
    text = ''
    active = True
    clock = pygame.time.Clock()
    try:gw.getWindowsWithTitle("Entrez votre pseudo")[0].activate()  # First plan
    except:pass
    
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
    
    def timer(self):
            
        if len(gameVar.PLAYERS)==1: return
            
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
        
        if self.game_remaining_time==0:
            if self.me["is_drawer"]: #if game time over
                try:
                    loop = asyncio.get_running_loop()  # Essaie d'obtenir une boucle existante
                except RuntimeError:
                    loop = asyncio.new_event_loop()  # Crée une nouvelle boucle si aucune n'existe
                    asyncio.set_event_loop(loop)
                asyncio.run(gameVar.WS.send(json.dumps({"type":"game_finished"})))
            gameVar.GAMESTART=datetime.now()
            
        if self.game_remaining_time%10==0 and self.frame_num>=config["game_page_fps"]-1:# for keep connection
            if gameVar.WS: asyncio.run(gameVar.WS.ping())
    
    def players(self):
        pygame.draw.rect(self.screen, BLANC, (0.01 * self.W, 0.04 * self.H, 0.18 * self.W, 0.7 * self.H))
        pygame.draw.rect(self.screen, NOIR, (0.01 * self.W, 0.04 * self.H, 0.18 * self.W, 0.7 * self.H), 1)

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

        for y,player in enumerate(gameVar.PLAYERS):
            text_color=(10,10,10) if player["id"] == gameVar.PLAYER_ID else (100,100,100)

            pygame.draw.rect(self.screen, (222,0,0) if player["id"]==gameVar.CURRENT_DRAWER else (0,0,0),dico_co[y][1])
            pygame.draw.rect(self.screen, config["players_colors"][y],(dico_co[y][1][0]+3,dico_co[y][1][1]+3,dico_co[y][1][2]-6,dico_co[y][1][3]-6))
            font = pygame.font.Font("PermanentMarker.ttf" ,30)
            image_texte = font.render ( player["pseudo"], 1 , text_color )
            font = pygame.font.Font("PermanentMarker.ttf" ,20)
            self.screen.blit(image_texte, dico_co[y][0])
            image_texte = font.render ( "points:  "+str(player["points"]), 1 , text_color )
            self.screen.blit(image_texte, dico_co[y][2])

            if player["id"] != gameVar.CURRENT_DRAWER:
                image_texte = font.render ( "Trouvé ", 1 , text_color )
                self.screen.blit(image_texte, dico_co[y][4])
                    
                pygame.draw.circle(self.screen, text_color, dico_co[y][3], 7)
                if player["found"]:
                    pygame.draw.circle(self.screen, VERT,dico_co[y][3], 5)
                else:
                    pygame.draw.circle(self.screen, ROUGE,dico_co[y][3], 5)
    
    def sentence(self):
        pygame.draw.rect(self.screen, BLANC, (0.01 * self.W, 0.75 * self.H, 0.18 * self.W, 0.2 * self.H))
        pygame.draw.rect(self.screen, NOIR, (0.01 * self.W, 0.75 * self.H, 0.18 * self.W, 0.2 * self.H), 1)

        text= "Phrase à faire deviner:"if self.me["is_drawer"] else "Phrase à trouver:"
        pygame.draw.rect(self.screen, VERT,(1/100*self.W,75/100*self.H, 18/100*self.W, 20/100*self.H) )

        font = pygame.font.Font("PermanentMarker.ttf" ,22)
        image_texte = font.render ( text, 1 , (0,0,0) )
        self.screen.blit(image_texte, (2/100*self.W,77/100*self.H))
        
        if len(gameVar.CURRENT_SENTENCE) >0:
            FONT_SIZE_BASE = 20  # Taille de base de la font
            Y_START = 77 / 100 * self.H +36 # Position de départ

            # Choisir la taille de font en fonction de la longueur du texte
            if len(gameVar.CURRENT_SENTENCE) <= 30:
                font_size = FONT_SIZE_BASE
            elif len(gameVar.CURRENT_SENTENCE) <= 60:
                font_size = FONT_SIZE_BASE - 2
            else:
                font_size = FONT_SIZE_BASE - 4

            font = pygame.font.Font("PermanentMarker.ttf", font_size)

            lines=tools.lines_return(gameVar.CURRENT_SENTENCE, font, 0.16 * self.W)

            # Affichage ligne par ligne
            for i, ligne in enumerate(lines):
                image_texte = font.render(ligne, True, (20, 10, 10))
                if (not self.me["found"]) and not self.me["is_drawer"]:
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
        self.pixel_width = (zone_x_max - zone_x_min) // canvas_width
        self.pixel_height = (zone_y_max - zone_y_min) // canvas_height
        
        zone_x_min = self.W//2-self.pixel_width*canvas_width//2
        zone_x_max = self.W//2+self.pixel_width*canvas_width//2
        zone_y_min = self.H//2-self.pixel_height*canvas_height//2
        zone_y_max = self.H//2+self.pixel_height*canvas_height//2
        
        pygame.draw.rect(self.screen, NOIR, (zone_x_min-1, zone_y_min-1,zone_x_max-zone_x_min+2, zone_y_max-zone_y_min+2), 1)

        #! show
        for y in range(canvas_height):
            for x in range(canvas_width):
                color = gameVar.CANVAS[y][x] if gameVar.CANVAS[y][x] else BLANC
                pygame.draw.rect(self.screen, color, (zone_x_min + x * self.pixel_width, zone_y_min + y * self.pixel_height, self.pixel_width, self.pixel_height))

        #! drawing
<<<<<<< HEAD
        if zone_x_min <= self.mouse_pos[0] <= zone_x_max and zone_y_min <= self.mouse_pos[1] <= zone_y_max:# Vérifier si le clic est dans la zone de dessin
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    gameVar.ALL_FRAMES=tools.remove_steps_by_roll_back(gameVar.ALL_FRAMES, gameVar.ROLL_BACK)
                    gameVar.ROLL_BACK=0
                    self.second_draw_frames.append({"type":"new_step"})
                    gameVar.ALL_FRAMES.append({"type":"new_step"})
                    print("new step")
                    
                elif self.mouseDown and event.type == pygame.MOUSEMOTION:
                    if self.lastMouseDown and self.me["id"] == gameVar.CURRENT_DRAWER and 0<self.game_remaining_time<config["game_duration"]:   # can draw    
                        # Position actuelle dans le CANVAS
                        canvas_x = (event.pos[0] - zone_x_min) // self.pixel_width
                        canvas_y = (event.pos[1] - zone_y_min) // self.pixel_height
=======
        if self.me["is_drawer"]:
            if zone_x_min <= self.mouse_pos[0] <= zone_x_max and zone_y_min <= self.mouse_pos[1] <= zone_y_max:# Vérifier si le clic est dans la zone de dessin
                for event in self.events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        gameVar.ALL_FRAMES=tools.split_steps_by_roll_back(gameVar.ALL_FRAMES, gameVar.ROLL_BACK)[0]
                        gameVar.STEP_NUM=0
                        for frame in gameVar.ALL_FRAMES:
                            if frame["type"] in ["new_step", "shape"]:
                                gameVar.STEP_NUM+=1
                        
                        gameVar.ROLL_BACK=0
                        self.second_draw_frames.append({"type":"new_step"})
                        gameVar.ALL_FRAMES.append({"type":"new_step"})
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf

                        print("mouse down")
                        print("rollback",gameVar.ROLL_BACK)
                        print("step num",gameVar.STEP_NUM)

<<<<<<< HEAD
                            # Générer les points entre les deux
                            gameVar.CANVAS = tools.draw_brush_line(gameVar.CANVAS, x1, y1, x2, y2, self.pen_color, self.pen_radius)
                            self.second_draw_frames.append({"type":"draw","x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": self.pen_color, "radius": self.pen_radius})
                            gameVar.ALL_FRAMES.append({"type":"draw","x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": self.pen_color, "radius": self.pen_radius})

                        # Mettre à jour la dernière position
                        self.last_canvas_click = (canvas_x, canvas_y)
                                
                elif self.mouseDown and event.type == pygame.MOUSEBUTTONUP:
                    gameVar.STEP_NUM+=1
                                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):# CTRL+Z
                        gameVar.ROLL_BACK=min(gameVar.STEP_NUM,gameVar.ROLL_BACK+1)
                        
                        tools.update_canva_by_frames(gameVar.ALL_FRAMES, delay=False, reset=True)
                        
                    elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):# CTRL+Y
                        gameVar.ROLL_BACK=max(0,gameVar.ROLL_BACK-1)
                        
                        tools.update_canva_by_frames(gameVar.ALL_FRAMES, delay=False, reset=True)
=======
                        
                    elif self.mouseDown and event.type == pygame.MOUSEMOTION:
                        if self.lastMouseDown and 0<self.game_remaining_time<config["game_duration"]:   # can draw    
                            # Position actuelle dans le CANVAS
                            canvas_x = (event.pos[0] - zone_x_min) // self.pixel_width
                            canvas_y = (event.pos[1] - zone_y_min) // self.pixel_height

                            # Dessiner une ligne entre last_click et la position actuelle
                            if self.last_canvas_click and self.last_canvas_click != (canvas_x, canvas_y):
                                x1, y1 = self.last_canvas_click
                                x2, y2 = canvas_x, canvas_y

                                # Générer les points entre les deux
                                gameVar.CANVAS = tools.draw_brush_line(gameVar.CANVAS, x1, y1, x2, y2, self.pen_color, self.pen_radius, 0)
                                self.second_draw_frames.append({"type":"draw","x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": self.pen_color, "radius": self.pen_radius})
                                gameVar.ALL_FRAMES.append({"type":"draw","x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": self.pen_color, "radius": self.pen_radius})

                            # Mettre à jour la dernière position
                            self.last_canvas_click = (canvas_x, canvas_y)
                                    
                    elif event.type == pygame.MOUSEBUTTONUP:
                        gameVar.STEP_NUM+=1

                        print("mouse up")
                        print("rollback",gameVar.ROLL_BACK)
                        print("step num",gameVar.STEP_NUM)
                                    
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):# CTRL+Z

                            gameVar.ROLL_BACK=min(gameVar.STEP_NUM,gameVar.ROLL_BACK+1)
                            
                            tools.update_canva_by_frames(gameVar.ALL_FRAMES, delay=False, reset=True)

                            try:
                                loop = asyncio.get_running_loop()  # Essaie d'obtenir une boucle existante
                            except RuntimeError:
                                loop = asyncio.new_event_loop()  # Crée une nouvelle boucle si aucune n'existe
                                asyncio.set_event_loop(loop)
                            asyncio.run(gameVar.WS.send(json.dumps({"type":"roll_back","roll_back":gameVar.ROLL_BACK})))



                            print("undo")
                            print("rollback",gameVar.ROLL_BACK)
                            print("step num",gameVar.STEP_NUM)

                                
                        elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):# CTRL+Y

                            gameVar.ROLL_BACK=max(0,gameVar.ROLL_BACK-1)
                            
                            tools.update_canva_by_frames(gameVar.ALL_FRAMES, delay=False, reset=True)


                            try:
                                loop = asyncio.get_running_loop()  # Essaie d'obtenir une boucle existante
                            except RuntimeError:
                                loop = asyncio.new_event_loop()  # Crée une nouvelle boucle si aucune n'existe
                                asyncio.set_event_loop(loop)
                            asyncio.run(gameVar.WS.send(json.dumps({"type":"roll_back","roll_back":gameVar.ROLL_BACK})))


                            print("redo")
                            print("rollback",gameVar.ROLL_BACK)
                            print("step num",gameVar.STEP_NUM)
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
                    

        #send draw
        if self.frame_num==config["game_page_fps"]-1 and self.second_draw_frames!=[]:
<<<<<<< HEAD
=======
            print("envoi du draw", self.second_draw_frames)
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
            asyncio.run(tools.websocket_draw(gameVar.WS, self.second_draw_frames))  #send datas
            self.second_draw_frames=[]
        
    def couleurs(self):
        pygame.draw.rect(self.screen, BLANC, (0.81 * self.W, 0.04 * self.H, 0.18 * self.W, 0.25 * self.H))
        pygame.draw.rect(self.screen, NOIR, (0.81 * self.W, 0.04 * self.H, 0.18 * self.W, 0.25 * self.H), 1)

        """Affiche une palette de couleurs fixes et permet de sélectionner une couleur."""
        palette_x, palette_y = int(0.81 * self.W), int(0.04 * self.H)+6
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

    def slider_radius(self):
        pygame.draw.rect(self.screen, BLANC, (0.81 * self.W, 0.3083 * self.H, 0.18 * self.W, 0.0833 * self.H))
        pygame.draw.rect(self.screen, NOIR, (0.81 * self.W, 0.3083 * self.H, 0.18 * self.W, 0.0833 * self.H), 1)

        try: self.pixel_height #test la variable
        except: return
        
        slider_x, slider_y, slider_w, slider_h = (
            0.81 * self.W, 0.3083 * self.H, 0.18 * self.W, 0.0833 * self.H
        )
        slider_min = slider_x + 10
        slider_max = slider_x + slider_w - 10
        radius_slider_pos = slider_min + (self.pen_radius//self.pixel_height - 1) * (slider_max - slider_min) / 10

        # Fond du slider
        pygame.draw.rect(self.screen, (200,200,200), (slider_x, slider_y, slider_w, slider_h))
        
        # Barre de progression
        pygame.draw.line(self.screen, (0, 0, 0), (slider_min, slider_y + slider_h // 2), 
                         (slider_max, slider_y + slider_h // 2), 4)
        
        # Bouton du slider
        pygame.draw.circle(self.screen, (255, 180, 50), (int(radius_slider_pos), slider_y + slider_h // 2+1), self.pen_radius)
        
        # Cercle de prévisualisation (taille du crayon)
        #pygame.draw.circle(self.screen, self.pen_color, (int(slider_x) - 20, int(slider_y + slider_h // 2)), self.pen_radius)
        
        #update
        for event in self.events:
            if event.type == pygame.MOUSEMOTION and self.mouseDown:
                if slider_min-self.pen_radius<=event.pos[0]<=slider_max+self.pen_radius and slider_y <= event.pos[1] <= slider_y + slider_h:
                    radius_slider_pos = max(slider_min, min(event.pos[0], slider_max))
                    self.pen_radius = int((int(1 + (radius_slider_pos - slider_min) * 10 / (slider_max - slider_min)))* self.pixel_height)
                    

    def chat(self):

        font = pygame.font.Font("PermanentMarker.ttf" ,18)
        guess_line=tools.lines_return(self.guess, font, 0.15 * self.W)
        input_box = pygame.Rect(0.82 * self.W, 0.9533 * self.H-45 -len(guess_line)*20, 0.16 * self.W, max(40,15+20*len(guess_line)))
        
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.guess_input_active = input_box.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and self.guess_input_active:
                if event.key == pygame.K_RETURN and self.guess.strip():
                    try:
                        loop = asyncio.get_running_loop()  # Essaie d'obtenir une boucle existante
                    except RuntimeError:
                        loop = asyncio.new_event_loop()  # Crée une nouvelle boucle si aucune n'existe
                        asyncio.set_event_loop(loop)
                    asyncio.run(tools.send_message(gameVar.WS, self.guess,self.game_remaining_time))
                    gameVar.MESSAGES.append({"pseudo":self.me["pseudo"], "guess":self.guess, "succeed":False})
                    self.guess=""
                elif event.key == pygame.K_BACKSPACE:
                    self.guess = self.guess[:-1]
                else:
                    self.guess += event.unicode

        # Mise à jour visuelle
        min_y=0.4083 * self.H if self.me["is_drawer"] else 0.04 * self.H -45 -len(guess_line)*20
        pygame.draw.rect(self.screen, BLANC, (0.81 * self.W, min_y, 0.18 * self.W, 0.9533 * self.H - min_y))
        pygame.draw.rect(self.screen, NOIR, (0.81 * self.W, min_y, 0.18 * self.W, 0.9533 * self.H - min_y), 1)

        color = BLEU if self.guess_input_active else BLEU_CLAIR
        for i,line in enumerate(guess_line):
            txt_surface = font.render(line, True, NOIR)
            self.screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5+i*20))
        pygame.draw.rect(self.screen, color, input_box, 2)


        #chat
        y=0.9533 * self.H-60 -len(guess_line)*20

        for mess in gameVar.MESSAGES[::-1]:

            font = pygame.font.Font("PermanentMarker.ttf" ,16)
            if type(mess)==dict: #message formated
                if mess["succeed"]:

                    text=f"{mess['pseudo']} à trouvé (+{mess['points']} points)!"
                    color=(0,255,0)
                
                else:

                    text=mess["guess"]
                    color=(0,0,0)
            elif type(mess)==str:
                text=mess
                color=(0,50,210)

            # write the message
            lines=tools.lines_return(text, font, 0.16 * self.W)

            for line in lines[::-1]:
                if y>min_y+16:
                    y-=19

                    image_texte = font.render ( line, 1 , color)
                    self.screen.blit(image_texte, (0.82 * self.W,y))
            
            if y<min_y+18:
                break

            # write pseudo
            if type(mess)==dict and not mess["succeed"]:
                y-=20
                image_texte = font.render ( mess["pseudo"], 1 , (80,80,80) )
                self.screen.blit(image_texte, (0.82 * self.W + 30,y))

            y-=10

    
    def __init__(self):
        pygame.init()
        pygame.display.set_icon(pygame.image.load("icon.png"))
        
        # Dimensions de la fenêtre
        self.W, self.H = tools.get_screen_size()
        self.screen = pygame.display.set_mode((self.W,self.H))
        pygame.display.set_caption("Drawwy")
        try:gw.getWindowsWithTitle("Drawwy")[0].activate()  # First plan
        except:pass
        self.clock = pygame.time.Clock()
        self.clock.tick(config["game_page_fps"])
        
        self.game_remaining_time=config["game_duration"]
        
        self.me={   "id": -1,
                    "pseudo": "",
                    "points": 0,
                    "found":False,
                    "is_drawer":False
                    }
        
        #pen values
        self.pen_color=(0,0,0)
        self.pen_radius=6
        self.mouseDown=False
        self.lastMouseDown=False
        self.last_canvas_click=None
        
        self.mouse_pos=(0,0)
        
        #for drawing
        self.second_draw_frames=[]
        
        self.frame_num=0
        
        self.guess_input_active=False
        self.guess=""
        
        self.running = True
        while self.running:

            for player in gameVar.PLAYERS:
                if player["id"] == gameVar.PLAYER_ID:
                    self.me=player
                    self.me["is_drawer"]=gameVar.PLAYER_ID==gameVar.CURRENT_DRAWER
                    break

            if self.frame_num%2==0:
                self.game_remaining_time=(gameVar.GAMESTART+timedelta(seconds=config["game_duration"])-datetime.now()).seconds%config["game_duration"] if gameVar.GAMESTART else config["game_duration"]
                
                if gameVar.GAMESTART:
                    pass#print(gameVar.GAMESTART+timedelta(seconds=config["game_duration"]), datetime.now(), self.game_remaining_time)
            
            self.events=pygame.event.get()
            
            self.screen.fill(BEIGE)

            self.players()
            self.sentence()
            self.drawing()
            self.chat()
            if self.me["id"]==gameVar.PLAYER_ID:
                self.couleurs()
                self.slider_radius()
            self.timer()
            
            for event in self.events:
                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_q and not self.guess_input_active) or event.key == pygame.QUIT:
                        pygame.quit()
                        return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouseDown=True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseDown=False
                    self.last_canvas_click=None
                if event.type == pygame.MOUSEMOTION:
                    self.mouse_pos=event.pos
                    if self.mouseDown:
                        self.lastMouseDown=self.mouseDown
            
            pygame.display.flip()
            
            self.frame_num=(self.frame_num+1)%config["game_page_fps"]
            self.clock.tick(config["game_page_fps"])