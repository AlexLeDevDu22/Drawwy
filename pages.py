import pygame
import sys
import tools
import gameVar
import yaml
import tools
import asyncio

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
    
    def players(self):
        police = pygame.font.Font("PermanentMarker.ttf" ,20)
        image_texte = police.render ( "Liste de joueurs:", 1 , (0,0,0) )
        self.screen.blit(image_texte, (5.5/100*self.W,6/100*self.H))


        dico_co = [
            [(5/100*self.W,(12.5+i*7)/100*self.H),
             (1/100*self.W, (11+i*7)/100*self.H, 18/100*self.W, 7/100*self.H),
             (12/100*self.W,(14+i*7)/100*self.H),
             (17.4/100*self.W,(13.2+i*7)/100*self.H),
             (12/100*self.W,(12+i*7)/100*self.H)]
            for i in range(9)  # Génère 9 entrées automatiquement
        ]

        for y,player in enumerate(gameVar.PLAYERS):

            pygame.draw.rect(self.screen, (222,0,0) if player["id"]==0 else (0,0,0),dico_co[y][1])
            pygame.draw.rect(self.screen, config["players_colors"][y],(dico_co[y][1][0]+3,dico_co[y][1][1]+3,dico_co[y][1][2]-6,dico_co[y][1][3]-6))
            police = pygame.font.Font("PermanentMarker.ttf" ,30)
            image_texte = police.render ( player["pseudo"], 1 , (0,0,0) )
            police = pygame.font.Font("PermanentMarker.ttf" ,20)
            self.screen.blit(image_texte, dico_co[y][0])
            image_texte = police.render ( "points:    "+str(player["points"]), 1 , (0,0,0) )
            self.screen.blit(image_texte, dico_co[y][2])

            image_texte = police.render ( "Trouvé ", 1 , (0,0,0) )
            self.screen.blit(image_texte, dico_co[y][4])
            pygame.draw.circle(self.screen, NOIR, dico_co[y][3], 7)
            if player["found"]:
                pygame.draw.circle(self.screen, VERT,dico_co[y][3], 5)
            else:
                pygame.draw.circle(self.screen, ROUGE,dico_co[y][3], 5)
    
    def sentence(self):
        pygame.draw.rect(self.screen, VERT,(1/100*self.W,75/100*self.H, 18/100*self.W, 20/100*self.H) )

        police = pygame.font.Font("PermanentMarker.ttf" ,20)
        image_texte = police.render ( "Mot à faire deviner:", 1 , (0,0,0) )
        self.screen.blit(image_texte, (4/100*self.W,77/100*self.H))
        
        if len(gameVar.CURRENT_SENTENCE) >0:
            MAX_LARGEUR = 20  # Nombre max de caractères par ligne (ajuste si besoin)
            FONT_SIZE_BASE = 22  # Taille de base de la police
            Y_START = 77 / 100 * self.H +36 # Position de départ

            # Choisir la taille de police en fonction de la longueur du texte
            if len(gameVar.CURRENT_SENTENCE) <= MAX_LARGEUR:
                font_size = FONT_SIZE_BASE
            elif len(gameVar.CURRENT_SENTENCE) <= 2 * MAX_LARGEUR:
                font_size = FONT_SIZE_BASE - 2
            else:
                font_size = FONT_SIZE_BASE - 4

            police = pygame.font.Font("PermanentMarker.ttf", font_size)

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
                image_texte = police.render(ligne, True, (0, 0, 0))
                if not self.me["found"] or self.me["id"] != gameVar.CURRENT_DRAWER:
                    image_texte=tools.flou(image_texte)
                self.screen.blit(image_texte, (0.03 * self.W, Y_START + (i * (font_size + 2))))
                
    def drawing(self):
        """Permet de dessiner uniquement dans la zone de dessin."""
        if not gameVar.CANVAS:
            return
        
        
        zone_x_min = int(0.2 * self.W)+2  # 20% de la largeur de la fenêtre
        zone_x_max = int(0.8 * self.W)+2  # 60% de la largeur de la fenêtre
        zone_y_min = int(0.04 * self.H)   # Commence en haut de la fenêtre
        zone_y_max = int(0.96 * self.H)   # Remplie toute la hauteur de la fenêtre
        
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
        for event in self.events:
            if self.mouseDown and event.type==pygame.MOUSEMOTION:
                # Vérifier si le clic est dans la zone de dessin
                if zone_x_min <= event.pos[0] <= zone_x_max and zone_y_min <= event.pos[1] <= zone_y_max:
                    self.is_drawing = True
                    # Calculer la position du clic dans le tableau CANVAS
                    canvas_x = (event.pos[0] - zone_x_min) * canvas_width // (zone_x_max - zone_x_min)
                    canvas_y = (event.pos[1] - zone_y_min) * canvas_height // (zone_y_max - zone_y_min)
                    tools.draw_canvas(gameVar.CANVAS, canvas_x, canvas_y, self.pen_color, self.pen_radius)  # Dessiner un pixel noir
                    
                    asyncio.run(tools.websocket_draw(gameVar.WS, canvas_x, canvas_y, self.pen_color, self.pen_radius))  #send datas

    def couleurs(self):
        """Affiche une palette de couleurs fixes et permet de sélectionner une couleur."""
        palette_x, palette_y = int(0.81 * self.W), int(0.04 * self.H)
        palette_w, palette_h = int(0.18 * self.W), int(0.25 * self.H)

        
        # Taille des carrés de couleur
        cols = 4  # Nombre de couleurs par ligne
        square_size = min(palette_w // cols, palette_h // (len(config["drawing_colors"]) // cols + 1))
        
        for i, color in enumerate(config["drawing_colors"]):
            row = i // cols
            col = i % cols
            x = palette_x + col * (square_size+10)  +(palette_w-(square_size+10)*4)//2
            y = palette_y + row * (square_size+10)
            pygame.draw.rect(self.screen, color, (x, y, square_size, square_size))
            pygame.draw.rect(self.screen, (0, 0, 0), (x, y, square_size, square_size), 2)  # Bordure noire

        # Afficher la couleur sélectionnée
        selected_x = palette_x + palette_w // 2 - 50
        selected_y = palette_y + palette_h -15
        pygame.draw.rect(self.screen, self.pen_color, (selected_x, selected_y, 100, 30))
        pygame.draw.rect(self.screen, (0, 0, 0), (selected_x, selected_y, 100, 30), 2)  # Bordure noire
        
        
        #! click on color
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                for i, color in enumerate(config["drawing_colors"]):
                    row = i // cols
                    col = i % cols
                    x = palette_x + col * (square_size+10)
                    y = palette_y + row * (square_size+10)
                    if x <= mouse_x < x + square_size and y <= mouse_y < y + square_size:
                        self.pen_color = color

    def chat(self):
        (0.81 * self.W, 0.4083 * self.H, 0.18 * self.W, 0.545 * self.H),  # Chat
        
        for mess in gameVar.MESSAGES:
            police = pygame.font.Font("PermanentMarker.ttf" ,15)
            image_texte = police.render ( mess["pseudo"], 1 , (80,80,80) )
            self.screen.blit(image_texte, (0.82 * self.W + 30, 0.41 * self.H))
            police = pygame.font.Font("PermanentMarker.ttf" ,12)
            image_texte = police.render ( mess["guess"], 1 , (0,0,0) )
            self.screen.blit(image_texte, (0.82 * self.W, 0.41 * self.H + 20))
    
    def __init__(self):
        pygame.init()
        
        # Dimensions de la fenêtre
        self.W, self.H = tools.get_screen_size()
        self.screen = pygame.display.set_mode((self.W,self.H))
        pygame.display.set_caption("UIdrawer")
        self.clock = pygame.time.Clock()
        self.clock.tick(30)
        
        #pen values
        self.pen_color=(0,0,0)
        self.pen_radius=1
        self.mouseDown=False
        
        self.me={   "id": -1,
                    "pseudo": "",
                    "points": 0,
                    "found":False,}
        self.running = True
        while self.running:
            
            for player in gameVar.PLAYERS:
                if player["id"] == gameVar.PLAYER_ID:
                    self.me=player #my data
            
            self.events=pygame.event.get()
            
            self.background()
            self.players()
            self.sentence()
            self.drawing()
            self.chat()
            self.couleurs()
            
            for event in self.events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.QUIT:
                        self.running=False    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouseDown=True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseDown=False
                    
            pygame.display.flip()