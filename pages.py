import pygame
import sys
import tools
import gameVar
import yaml
import tools

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
        police = pygame.font.SysFont("serif " ,20)
        image_texte = police.render ( "Liste de joueurs:", 1 , (0,0,0) )
        self.screen.blit(image_texte, (5.5/100*self.W,6/100*self.H))


        dico_co = [
            [(5.5/100*self.W,(12.5+i*7)/100*self.H),
             (1/100*self.W, (11+i*7)/100*self.H, 18/100*self.W, 7/100*self.H),
             (12/100*self.W,(14+i*7)/100*self.H),
             (17.4/100*self.W,(13.2+i*7)/100*self.H),
             (12/100*self.W,(12+i*7)/100*self.H)]
            for i in range(9)  # Génère 9 entrées automatiquement
        ]

        for y,player in enumerate(gameVar.PLAYERS):

            pygame.draw.rect(self.screen, (222,0,0) if player["id"]==0 else (0,0,0),dico_co[y][1])
            pygame.draw.rect(self.screen, config["players_colors"][y],(dico_co[y][1][0]+3,dico_co[y][1][1]+3,dico_co[y][1][2]-6,dico_co[y][1][3]-6))
            police = pygame.font.SysFont("serif " ,30)
            image_texte = police.render ( player["pseudo"], 1 , (0,0,0) )
            police = pygame.font.SysFont("serif " ,20)
            self.screen.blit(image_texte, dico_co[y][0])
            image_texte = police.render ( "points:    "+str(player["points"]), 1 , (0,0,0) )
            self.screen.blit(image_texte, dico_co[y][2])

            image_texte = police.render ( "Trouvé ? ", 1 , (0,0,0) )
            self.screen.blit(image_texte, dico_co[y][4])
            pygame.draw.circle(self.screen, NOIR, dico_co[y][3], 7)
            if gameVar.FOUND == True:
                pygame.draw.circle(self.screen, VERT,dico_co[y][3], 5)
            else:
                pygame.draw.circle(self.screen, ROUGE,dico_co[y][3], 5)
    
    def sentence(self):
        pygame.draw.rect(self.screen, VERT,(1/100*self.W,75/100*self.H, 18/100*self.W, 20/100*self.H) )

        police = pygame.font.SysFont("serif " ,20)
        image_texte = police.render ( "Mot à faire deviner:", 1 , (0,0,0) )
        self.screen.blit(image_texte, (5/100*self.W,77/100*self.H))
        
        if len(gameVar.CURRENT_SENTENCE) >0:
            MAX_LARGEUR = 20  # Nombre max de caractères par ligne (ajuste si besoin)
            FONT_SIZE_BASE = 22  # Taille de base de la police
            Y_START = 80 / 100 * self.H  # Position de départ

            # Choisir la taille de police en fonction de la longueur du texte
            if len(gameVar.CURRENT_SENTENCE) <= MAX_LARGEUR:
                font_size = FONT_SIZE_BASE
            elif len(gameVar.CURRENT_SENTENCE) <= 2 * MAX_LARGEUR:
                font_size = FONT_SIZE_BASE - 2
            else:
                font_size = FONT_SIZE_BASE - 4

            police = pygame.font.SysFont("monospace", font_size)

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
                if not gameVar.FOUND:
                    image_texte=tools.flou(image_texte)
                self.screen.blit(image_texte, (0.03 * self.W, Y_START + (i * (font_size + 2))))
def drawing(self):
    """Permet de dessiner uniquement dans la zone de dessin."""
    drawing_zone = self.zones[0]  # Première zone définie comme zone de dessin
    x_min, y_min, width, height = drawing_zone
    x_max, y_max = x_min + width, y_min + height

    drawing = False
    last_pos = None
    color = NOIR  # Couleur du trait

    while self.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if x_min <= event.pos[0] <= x_max and y_min <= event.pos[1] <= y_max:
                    drawing = True
                    last_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                drawing = False
            elif event.type == pygame.MOUSEMOTION and drawing:
                if x_min <= event.pos[0] <= x_max and y_min <= event.pos[1] <= y_max:
                    pygame.draw.line(self.screen, color, last_pos, event.pos, 3)
                    last_pos = event.pos

        pygame.display.flip()


    
    def chat(self):
        (0.81 * self.W, 0.4083 * self.H, 0.18 * self.W, 0.545 * self.H),  # Chat
        
        for mess in gameVar.MESSAGES:
            police = pygame.font.SysFont("serif " ,15)
            image_texte = police.render ( mess["guess"], 1 , (0,0,0) )
            self.screen.blit(image_texte, (0.83 * self.W, 0.41 * self.H))
            image_texte = police.render ( mess["pseudo"], 1 , (0,0,0) )
            self.screen.blit(image_texte, (0.83 * self.W, 0.38 * self.H))
    
    def __init__(self):
        pygame.init()
        
        # Dimensions de la fenêtre
        self.W, self.H = tools.get_screen_size()
        self.screen = pygame.display.set_mode((self.W,self.H))
        pygame.display.set_caption("UIdrawer")
        self.clock = pygame.time.Clock()
        self.clock.tick(30)
        
        
        self.running = True
        while self.running:
            
            self.background()
            self.players()
            self.sentence()
            self.chat()
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q or event.key == pygame.QUIT:
                        self.running=False
                    
            pygame.display.flip()