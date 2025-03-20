from shared.utils.data_manager import *
import time
import pygame
import sys
import time
import os

pygame.init()

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

class SoloGame:
    

         
    def drawing(self):
        zone_x_min = int(0.2 * self.W) + 2
        zone_x_max = int(0.8 * self.W) - 4
        zone_y_min = int(0.04 * self.H) + 2
        zone_y_max = int(0.96 * self.H) - 4

        canvas_width = int(zone_x_max - zone_x_min)
        canvas_height = int(zone_y_max - zone_y_min)

        # Initialisation correcte du CANVAS en 2D
        CANVAS = [[BLANC for _ in range(canvas_width)] for _ in range(canvas_height)]

        # Affichage du CANVAS à l'écran
        self.pixel_width = (zone_x_max - zone_x_min) // canvas_width
        self.pixel_height = (zone_y_max - zone_y_min) // canvas_height

        zone_x_min = self.W // 2 - self.pixel_width * canvas_width // 2
        zone_x_max = self.W // 2 + self.pixel_width * canvas_width // 2
        zone_y_min = self.H // 2 - self.pixel_height * canvas_height // 2
        zone_y_max = self.H // 2 + self.pixel_height * canvas_height // 2

        pygame.draw.rect(self.screen, NOIR, (zone_x_min - 1, zone_y_min - 1, zone_x_max - zone_x_min + 2, zone_y_max - zone_y_min + 2), 1)

        # Affichage du CANVAS
        for y in range(canvas_height):
            for x in range(canvas_width):
                color = CANVAS[y][x] if CANVAS[y][x] else BLANC
                pygame.draw.rect(self.screen, color, (zone_x_min + x * self.pixel_width, zone_y_min + y * self.pixel_height, self.pixel_width, self.pixel_height))

        # Vérification de la zone de dessin
        if zone_x_min <= self.mouse_pos[0] <= zone_x_max and zone_y_min <= self.mouse_pos[1] <= zone_y_max:
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:



                    ROLL_BACK = 0
                    self.second_draw_frames.append({"type": "new_step"})

                elif self.mouseDown and event.type == pygame.MOUSEMOTION:
                    if self.lastMouseDown:
                        canvas_x = (event.pos[0] - zone_x_min) // self.pixel_width
                        canvas_y = (event.pos[1] - zone_y_min) // self.pixel_height

                        if self.last_canvas_click and self.last_canvas_click != (canvas_x, canvas_y):
                            x1, y1 = self.last_canvas_click
                            x2, y2 = canvas_x, canvas_y

                            CANVAS = tools.draw_brush_line(CANVAS, x1, y1, x2, y2, self.pen_color, self.pen_radius, 0)
                            self.second_draw_frames.append({"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": self.pen_color, "radius": self.pen_radius})
            

                        self.last_canvas_click = (canvas_x, canvas_y)

    def couleurs(self):
        pygame.draw.rect(self.screen, BLANC, (0.81 * self.W, 0.04 * self.H, 0.18 * self.W, 0.25 * self.H))
        pygame.draw.rect(self.screen, NOIR, (0.81 * self.W, 0.04 * self.H, 0.18 * self.W, 0.25 * self.H), 1)

        """Affiche une palette de couleurs fixes et permet de sélectionner une couleur."""
        palette_x, palette_y = int(0.81 * self.W), int(0.04 * self.H)+6
        palette_w, palette_h = int(0.18 * self.W), int(0.25 * self.H)

        # Taille des carrés de couleur
        cols = 4  # Nombre de couleurs par ligne
        square_size = min(palette_w // cols, palette_h // (len(CONFIG["drawing_colors"]) // cols + 1))
        spacing = 10  # Espacement entre les couleurs
        offset_x = (palette_w - (square_size + spacing) * cols) // 2  # Centrage horizontal

        for i, color in enumerate(CONFIG["drawing_colors"]):
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
                for i, color in enumerate(CONFIG["drawing_colors"]):
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
                    

    
    def __init__(self,screen,clock, W,H):

        self.screen, self.W, self.H=screen, W,H
        self.connected=False
        
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
        
        while 1:
            clock.tick(CONFIG["fps"])


            
            self.events=pygame.event.get()
            
            self.screen.fill(BEIGE)

            self.couleurs()
            self.slider_radius()
            self.drawing()
            
            for event in self.events:
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_q and not self.guess_input_active) or event.type == pygame.QUIT:
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
                if event.type == pygame.VIDEORESIZE:
                    self.W, self.H = tools.get_screen_size()
            
            pygame.display.flip()
            
            self.frame_num=(self.frame_num+1)%50


        os._exit(0)