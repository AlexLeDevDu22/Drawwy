import pygame
import sys

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.common_ui import *
from shared.tools import *

#les configs
config = {
    "game_page_fps": 120,
    "drawing_colors": [
        (255,0,0),   (0,255,0),   (0,0,255),   (255,255,0),
        (255,165,0), (128,0,128), (0,0,0),     (255,255,255),
        (0,255,255), (255,0,255), (165,42,42), (128,128,128)
    ]
}
def get_screen_size():
    info_ecran = pygame.display.Info()
    return info_ecran.current_w, info_ecran.current_h

class SoloGame:
    def __init__(self, screen):
        self.last_mouse_pos = None 

        self.screen = screen
        self.W, self.H = screen.get_size()

        # Paramètres du pinceau
        self.pen_color = BLACK
        self.pen_radius = 6
        
        # État de la souris
        self.mouseDown = False
        self.mouse_pos = (0, 0)

        # On définit les valeurs des rectangles d’interface
        self.define_layout()

        # Canvas persistant (Surface)
        self.canvas_surf = pygame.Surface((self.canvas_rect.width, self.canvas_rect.height))
        self.canvas_surf.fill(WHITE)

        # Boucle principale
        clock = pygame.time.Clock()
        running = True
        while running:
            clock.tick(config["game_page_fps"])
            self.events = pygame.event.get()

            # Mise à jour de la taille si on redimensionne
            self.W, self.H = get_screen_size()
            self.define_layout()

            # Gestion des événements
            for event in self.events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouseDown = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouseDown = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos

            # Dessin de l’arrière-plan
            self.screen.fill(BEIGE)

            # Dessin du canvas au centre
            self.draw_canvas()

            # Dessin de la palette en haut à droite
            self.draw_colors()

            # Dessin du slider en dessous
            self.draw_slider()

            # Dessin du bouton "Valider" en bas à droite
            self.draw_validate_button()

            pygame.display.flip()

    def define_layout(self):

        # Canvas 
        self.canvas_rect = pygame.Rect(
            int(0.05 * self.W),    # marge à gauche
            int(0.05 * self.H),    # marge en haut
            int(0.70 * self.W),    # 70% de la largeur
            int(0.90 * self.H)     # 90% de la hauteur
        )

        # Palette 
        palette_width  = int(0.25 * self.W)
        palette_height = int(0.30 * self.H)
        self.colors_rect = pygame.Rect(
            self.canvas_rect.right + 10,
            int(0.05 * self.H),
            palette_width - 20,
            palette_height
        )

        # Le truc qui permet de changer la taille
        slider_width  = palette_width - 20
        slider_height = int(0.10 * self.H)
        self.slider_rect = pygame.Rect(
            self.canvas_rect.right + 10,
            self.colors_rect.bottom + 70,
            slider_width,
            slider_height
        )

        # Valider
        validate_button_w = 365
        validate_button_h = 50
        self.validate_button_rect = pygame.Rect(
            self.W - validate_button_w - 10,  # 20 px de marge à droite
            self.H - validate_button_h -400,  # 20 px de marge en bas
            validate_button_w,
            validate_button_h
        )

    def draw_canvas(self):
        # Cadre du canvas
        pygame.draw.rect(self.screen, BLACK, self.canvas_rect, 2)

        # On blit la Surface du canvas
        self.screen.blit(self.canvas_surf, (self.canvas_rect.x, self.canvas_rect.y))

        # Si la souris est enfoncée dans la zone du canvas, on dessine
        if self.mouseDown and self.canvas_rect.collidepoint(self.mouse_pos):
            # Coordonnées locales dans la surface
            local_x = self.mouse_pos[0] - self.canvas_rect.x
            local_y = self.mouse_pos[1] - self.canvas_rect.y
            # Dessin d'un cercle
            pygame.draw.circle(self.canvas_surf, self.pen_color, (local_x, local_y), self.pen_radius)

    def draw_colors(self):
        # Fond + bordure
        pygame.draw.rect(self.screen, (230,230,230), self.colors_rect)
        pygame.draw.rect(self.screen, BLACK, self.colors_rect, 2)

        margin = 10
        cols = 4
        rows = 3
        rect_w = (self.colors_rect.width - (cols+1)*margin) // cols
        rect_h = (self.colors_rect.height - (rows+1)*margin) // rows

        palette_colors = config["drawing_colors"]
        
        for i, color in enumerate(palette_colors[:12]):
            r = i // cols
            c = i % cols
            x = self.colors_rect.x + margin + c*(rect_w+margin)
            y = self.colors_rect.y + margin + r*(rect_h+margin)
            rect_color = pygame.Rect(x, y, rect_w, rect_h)

            # Dessin du carré de couleur
            pygame.draw.rect(self.screen, color, rect_color)
            pygame.draw.rect(self.screen, BLACK, rect_color, 2)

            # Gestion du clic
            if self.mouseDown and rect_color.collidepoint(self.mouse_pos):
                self.pen_color = color

        # Affiche la couleur sélectionnée sous la palette (vous pouvez essaye de le mettre dedans mais j'ai un peu galere...)
        color_bar = pygame.Rect(
            self.colors_rect.x + margin,
            self.colors_rect.bottom - margin + 20,
            self.colors_rect.width - 2*margin,
            50
        )
        pygame.draw.rect(self.screen, self.pen_color, color_bar)
        pygame.draw.rect(self.screen, BLACK, color_bar, 2)

    def draw_slider(self):
        """Dessine un slider simple sous la palette pour régler la taille du pinceau."""
        pygame.draw.rect(self.screen, (220,220,220), self.slider_rect)
        pygame.draw.rect(self.screen, BLACK, self.slider_rect, 2)

        # Barre du slider
        margin = 15
        line_y = self.slider_rect.centery
        line_start = (self.slider_rect.x + margin, line_y)
        line_end   = (self.slider_rect.right - margin, line_y)
        pygame.draw.line(self.screen, BLACK, line_start, line_end, 3)

        # Calcul de la position du bouton sur la barre
        max_radius = 50  # Rayon maximum pour le pinceau
        total_width = line_end[0] - line_start[0]
        ratio = self.pen_radius / max_radius
        knob_x = int(line_start[0] + ratio * total_width)
        knob_y = line_y

        # Ici, le knob est directement proportionnel à la taille du pinceau
        knob_size = self.pen_radius  # Taille proportionnelle
        pygame.draw.circle(self.screen, RED, (knob_x, knob_y), knob_size)

        # Gestion du clic pour modifier la taille du pinceau
        if self.mouseDown:
            mx, my = self.mouse_pos
            if self.slider_rect.collidepoint(mx, my):
                # On borne la position entre line_start et line_end
                knob_x = max(line_start[0], min(mx, line_end[0]))
                self.pen_radius = int(((knob_x - line_start[0]) / total_width) * max_radius)
                if self.pen_radius < 1:
                    self.pen_radius = 1
    def draw_validate_button(self):
        # Fond du bouton
        pygame.draw.rect(self.screen, (0, 255, 0), self.validate_button_rect)
        # Bordure noire
        pygame.draw.rect(self.screen, BLACK, self.validate_button_rect, 2)

        # Texte du bouton
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render("Valider", True, BLACK)
        text_rect = text_surface.get_rect(center=self.validate_button_rect.center)
        self.screen.blit(text_surface, text_rect)

        # Si on clique sur le bouton, on quitte (c ce truc a changer pour se rediriger mais pour l'instant il y a rien a rediriger)
        if self.mouseDown and self.validate_button_rect.collidepoint(self.mouse_pos):
            pygame.quit()
            sys.exit()

if __name__ == '__main__':
    W, H = get_screen_size()
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    SoloGame(screen)
