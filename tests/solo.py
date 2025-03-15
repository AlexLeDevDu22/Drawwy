import pygame
import sys
import math
import random
import time
from pygame import gfxdraw

from shared.ui.common_ui import *
from shared.ui.elements import *

W,H = pygame.display.Info().current_w, pygame.display.Info().current_h

class Button:
    def __init__(self, x, y, w=None, h=None, text=None, radius=40, circle=False, text_font=BUTTON_FONT, image=None, active=True):
        if not circle:
            self.W = w if w else text_font.size(text)[0] + 16
            self.H = h if h else text_font.size(text)[1] + 40
        else:
            self.W, self.H = radius * 2, radius * 2
        
        self.X = (pygame.display.Info().current_w - self.W) // 2 if x == "center" else x
        self.Y = (pygame.display.Info().current_h - self.H) // 2 if y == "center" else y
        self.rect = pygame.Rect(self.X, self.Y, self.W, self.H)
        self.offsets = 5
        self.text = text
        self.text_font = text_font
        self.hover = False
        self.radius = radius
        self.image = image
        self.circle = circle
        self.active = active
        self.disabled_color = HIDED_ORANGE  # Gris pour les boutons désactivés
        self.shadow_offset = 5

    def draw(self, screen):
        color = SOFT_ORANGE if self.hover else (ORANGE if self.active else self.disabled_color)
        shadow_color = DARK_BEIGE if self.active else (100, 100, 100)
        text_color = BLACK if self.active else (120, 120, 120)

        # Ombre
        pygame.draw.rect(screen, shadow_color, (self.X + self.shadow_offset, self.Y + self.shadow_offset, self.W, self.H), border_radius=self.radius)
        
        # Bouton principal
        pygame.draw.rect(screen, color, (self.X, self.Y, self.W, self.H), border_radius=self.radius)
        
        if self.text:
            # Texte
            draw_text(self.text, self.text_font, text_color, screen, self.X + self.W // 2, self.Y + self.H // 2 - (2 if self.hover else 0))
        elif self.image:
            # Image
            image = pygame.image.load(self.image)
            image = pygame.transform.smoothscale(image, (int(self.W * 0.7), int(self.H * 0.7)))
            image.set_alpha(255 if self.active else 180)  # Réduction d'opacité si désactivé
            screen.blit(image, (self.X + self.W * 0.15, self.Y + self.H * 0.15))

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos) and self.active
        return self.hover


class FloatingObject:
    def __init__(self, x, y, size, color, speed):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.orig_y = y
        self.amplitude = random.uniform(20, 50)
        self.phase = random.uniform(0, 2 * math.pi)
    
    def update(self):
        self.x += self.speed
        self.phase += 0.02
        self.y = self.orig_y + math.sin(self.phase) * self.amplitude
        
        if self.x > W + 100:
            self.x = -100
    
    def draw(self, surface):
        # Dessiner un cercle flou
        for i in range(5):
            radius = self.size - i
            alpha = 100 - i * 20
            gfxdraw.filled_circle(surface, int(self.x), int(self.y), radius, (*self.color, alpha))

# Supposons que Button et FloatingObject sont importés d'un autre fichier
# from other import Button, FloatingObject

# Initialisation de Pygame
pygame.init()
pygame.font.init()

# Constantes
WIDTH, HEIGHT = 1280, 720
TITLE = "Drawwy - Le jeu de dessin"
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
PURPLE = (130, 94, 196)
LIGHT_PURPLE = (157, 127, 211)
DARK_PURPLE = (103, 72, 158)
PINK = (255, 130, 186)
YELLOW = (255, 223, 97)
BLUE = (97, 190, 255)
GREEN = (97, 255, 162)
LIGHT_BLUE = (119, 181, 254)
VERY_LIGHT_BLUE = (160, 205, 255)
GREY = (200, 200, 200)
LIGHT_GREY = (230, 230, 230)
DARK_GREY = (100, 100, 100)

# Configuration de la fenêtre
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Chargement des polices
try:
    title_font = pygame.font.Font(None, 120)
    subtitle_font = pygame.font.Font(None, 70)
    theme_font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 40)
    info_font = pygame.font.Font(None, 30)
    timer_font = pygame.font.Font(None, 80)
except:
    print("Erreur lors du chargement des polices. Utilisation des polices par défaut.")
    title_font = pygame.font.SysFont('Arial', 120)
    subtitle_font = pygame.font.SysFont('Arial', 70)
    theme_font = pygame.font.SysFont('Arial', 50)
    button_font = pygame.font.SysFont('Arial', 40)
    info_font = pygame.font.SysFont('Arial', 30)
    timer_font = pygame.font.SysFont('Arial', 80)

class DrawingPage:
    def __init__(self, model_image, theme_name, theme_color):
        self.W = WIDTH
        self.H = HEIGHT
        self.screen = screen
        self.model_image = model_image
        self.theme_name = theme_name
        self.theme_color = theme_color
        
        # État du dessin
        self.mouseDown = False
        self.mouse_pos = (0, 0)
        self.pen_color = BLACK
        self.pen_radius = 5
        self.eraser_mode = False
        self.clear_confirm = False
        
        # Surface pour le dessin
        self.canvas_surf = pygame.Surface((int(0.70 * self.W), int(0.90 * self.H)))
        self.canvas_surf.fill(WHITE)
        
        # Palette de couleurs prédéfinies
        self.colors = [
            BLACK, WHITE, RED, GREEN, BLUE, YELLOW, PINK, PURPLE,
            (165, 42, 42),    # Marron
            (255, 165, 0),    # Orange
            (128, 0, 128),    # Violet
            (0, 128, 128),    # Teal
            (255, 192, 203),  # Rose pâle
            (0, 255, 255),    # Cyan
            (255, 255, 0),    # Jaune vif
            (128, 128, 128)   # Gris
        ]
        
        # Timer
        self.start_time = time.time()
        self.time_limit = 180  # 3 minutes
        
        # Création de la structure de l'interface
        self.define_layout()
        
        # Création des boutons
        self.create_buttons()
        
        # Objets flottants pour l'animation
        self.floating_objects = []
        for _ in range(10):
            x = random.randint(-100, WIDTH+100)
            y = random.randint(0, HEIGHT)
            size = random.randint(3, 10)
            color_choice = theme_color
            speed = random.uniform(0.1, 0.5)
            self.floating_objects.append(FloatingObject(x, y, size, color_choice, speed))

    def define_layout(self):
        # Zone de dessin principale
        self.canvas_rect = pygame.Rect(
            int(0.05 * self.W),    # marge à gauche
            int(0.12 * self.H),    # marge en haut
            int(0.60 * self.W),    # 60% de la largeur
            int(0.75 * self.H)     # 75% de la hauteur
        )
        
        # Zone du modèle
        self.model_rect = pygame.Rect(
            self.canvas_rect.right + 20,
            int(0.12 * self.H),
            int(0.30 * self.W),
            int(0.30 * self.H)
        )
        
        # Zone de la palette de couleurs
        self.colors_rect = pygame.Rect(
            self.canvas_rect.right + 20,
            self.model_rect.bottom + 20,
            int(0.30 * self.W),
            int(0.20 * self.H)
        )
        
        # Zone du slider pour taille du pinceau
        self.slider_rect = pygame.Rect(
            self.canvas_rect.right + 20,
            self.colors_rect.bottom + 20,
            int(0.30 * self.W),
            int(0.10 * self.H)
        )
        
        # Zone des outils (gomme, effacer tout)
        self.tools_rect = pygame.Rect(
            self.canvas_rect.right + 20,
            self.slider_rect.bottom + 20,
            int(0.30 * self.W),
            int(0.10 * self.H)
        )
        
        # Zone du bouton de validation
        self.validate_button_rect = pygame.Rect(
            self.canvas_rect.right + 20,
            self.H - int(0.10 * self.H) - 20,
            int(0.30 * self.W),
            int(0.07 * self.H)
        )
        
        # Zone du timer
        self.timer_rect = pygame.Rect(
            int(0.05 * self.W),
            int(0.02 * self.H),
            int(0.15 * self.W),
            int(0.08 * self.H)
        )

    def create_buttons(self):
        # Bouton de validation
        self.validate_button = Button(
            self.validate_button_rect.x,
            self.validate_button_rect.y,
            self.validate_button_rect.width,
            self.validate_button_rect.height,
            "Valider",
            GREEN,
            (150, 255, 150)
        )
        
        # Bouton gomme
        eraser_width = self.tools_rect.width * 0.45
        self.eraser_button = Button(
            self.tools_rect.x,
            self.tools_rect.y,
            eraser_width,
            self.tools_rect.height,
            "Gomme",
            LIGHT_GREY,
            WHITE
        )
        
        # Bouton effacer tout
        clear_width = self.tools_rect.width * 0.45
        self.clear_button = Button(
            self.tools_rect.x + eraser_width + 10,
            self.tools_rect.y,
            clear_width,
            self.tools_rect.height,
            "Effacer",
            LIGHT_GREY,
            WHITE
        )
        
        # Bouton pour annuler l'effacement
        self.cancel_clear_button = Button(
            WIDTH // 2 - 120,
            HEIGHT // 2 + 40,
            100,
            50,
            "Non",
            RED,
            (255, 150, 150)
        )
        
        # Bouton pour confirmer l'effacement
        self.confirm_clear_button = Button(
            WIDTH // 2 + 20,
            HEIGHT // 2 + 40,
            100,
            50,
            "Oui",
            GREEN,
            (150, 255, 150)
        )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouseDown = True
                
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseDown = False
                
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                
        # Si le temps est écoulé
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.time_limit:
            # On pourrait rediriger vers la page de résultats ici
            pass

    def update(self):
        # Mettre à jour les objets flottants
        for obj in self.floating_objects:
            obj.update()
            
        # Vérifier les clics sur les boutons
        if self.mouseDown:
            # Vérification du mode de confirmation d'effacement
            if self.clear_confirm:
                if self.cancel_clear_button.is_clicked(self.mouse_pos, (True, False, False)):
                    self.clear_confirm = False
                    self.mouseDown = False
                    
                elif self.confirm_clear_button.is_clicked(self.mouse_pos, (True, False, False)):
                    self.canvas_surf.fill(WHITE)
                    self.clear_confirm = False
                    self.mouseDown = False
                    
            # Vérification des autres boutons si pas en mode confirmation
            else:
                # Vérifier le bouton de validation
                if self.validate_button.is_clicked(self.mouse_pos, (True, False, False)):
                    print("Dessin validé!")
                    # Insérer le code pour passer à la page de résultats
                    self.mouseDown = False
                    
                # Vérifier le bouton gomme
                elif self.eraser_button.is_clicked(self.mouse_pos, (True, False, False)):
                    self.eraser_mode = not self.eraser_mode
                    self.mouseDown = False
                    
                # Vérifier le bouton effacer tout
                elif self.clear_button.is_clicked(self.mouse_pos, (True, False, False)):
                    self.clear_confirm = True
                    self.mouseDown = False
                    
        # Mettre à jour l'état de survol des boutons
        self.validate_button.check_hover(self.mouse_pos)
        self.eraser_button.check_hover(self.mouse_pos)
        self.clear_button.check_hover(self.mouse_pos)
        
        if self.clear_confirm:
            self.cancel_clear_button.check_hover(self.mouse_pos)
            self.confirm_clear_button.check_hover(self.mouse_pos)

    def draw(self):
        # Dessiner l'arrière-plan avec dégradé
        self.draw_background()
        
        # Dessiner les objets flottants
        for obj in self.floating_objects:
            obj.draw(screen)
        
        # Dessiner le titre
        self.draw_title()
        
        # Dessiner la zone de dessin
        self.draw_canvas()
        
        # Dessiner le modèle
        self.draw_model()
        
        # Dessiner la palette de couleurs
        self.draw_colors()
        
        # Dessiner le slider de taille
        self.draw_slider()
        
        # Dessiner les outils
        self.draw_tools()
        
        # Dessiner le bouton de validation
        self.validate_button.draw(screen)
        
        # Dessiner le timer
        self.draw_timer()
        
        # Si en mode de confirmation d'effacement
        if self.clear_confirm:
            self.draw_clear_confirmation()

    def draw_background(self):
        # Dégradé de fond bleu clair
        for y in range(self.H):
            # Interpolation entre deux couleurs pour créer un dégradé
            color = [
                int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / self.H))
                for i in range(3)
            ]
            pygame.draw.line(self.screen, color, (0, y), (self.W, y))

    def draw_title(self):
        # Dessiner le titre avec effet d'ombre
        title_text = "DRAWWY"
        title_shadow = title_font.render(title_text, True, BLACK)
        title_shadow_rect = title_shadow.get_rect(center=(self.W//2+3, 53))
        self.screen.blit(title_shadow, title_shadow_rect)
        
        title = title_font.render(title_text, True, WHITE)
        title_rect = title.get_rect(center=(self.W//2, 50))
        self.screen.blit(title, title_rect)

    def draw_canvas(self):
        # Dessiner un fond pour le canvas pour le mettre en évidence
        enlarged_rect = pygame.Rect(
            self.canvas_rect.x - 10,
            self.canvas_rect.y - 10,
            self.canvas_rect.width + 20,
            self.canvas_rect.height + 20
        )
        pygame.draw.rect(self.screen, LIGHT_GREY, enlarged_rect, border_radius=15)
        
        # Dessiner l'ombre du canvas
        shadow_rect = pygame.Rect(
            self.canvas_rect.x + 5,
            self.canvas_rect.y + 5,
            self.canvas_rect.width,
            self.canvas_rect.height
        )
        pygame.draw.rect(self.screen, DARK_GREY, shadow_rect, border_radius=10)
        
        # Dessiner le cadre du canvas
        pygame.draw.rect(self.screen, BLACK, self.canvas_rect, 2, border_radius=10)
        
        # Afficher la surface du canvas
        self.screen.blit(self.canvas_surf, (self.canvas_rect.x, self.canvas_rect.y))
        
        # Si la souris est enfoncée dans la zone du canvas, on dessine
        if self.mouseDown and self.canvas_rect.collidepoint(self.mouse_pos):
            # Coordonnées locales dans la surface
            local_x = self.mouse_pos[0] - self.canvas_rect.x
            local_y = self.mouse_pos[1] - self.canvas_rect.y
            
            if self.eraser_mode:
                pygame.draw.circle(self.canvas_surf, WHITE, (local_x, local_y), self.pen_radius)
            else:
                pygame.draw.circle(self.canvas_surf, self.pen_color, (local_x, local_y), self.pen_radius)

    def draw_model(self):
        pygame.draw.rect(self.screen, BLACK, self.model_rect, 2, border_radius=10)
        model_surf = pygame.image.load(self.model_image)
        model_surf = pygame.transform.scale(model_surf, (self.model_rect.width, self.model_rect.height))
        self.screen.blit(model_surf, (self.model_rect.x, self.model_rect.y))
        theme_text = theme_font.render(self.theme_name, True, self.theme_color)
        self.screen.blit(theme_text, (self.model_rect.x + 10, self.model_rect.y - 40))

    def draw_colors(self):
        pygame.draw.rect(self.screen, BLACK, self.colors_rect, 2, border_radius=10)
        col_size = 30
        padding = 10
        cols_per_row = self.colors_rect.width // (col_size + padding)
        for i, color in enumerate(self.colors):
            x = self.colors_rect.x + (i % cols_per_row) * (col_size + padding)
            y = self.colors_rect.y + (i // cols_per_row) * (col_size + padding)
            pygame.draw.rect(self.screen, color, (x, y, col_size, col_size), border_radius=5)
            if pygame.Rect(x, y, col_size, col_size).collidepoint(self.mouse_pos) and self.mouseDown:
                self.pen_color = color

    def draw_slider(self):
        pygame.draw.rect(self.screen, BLACK, self.slider_rect, 2, border_radius=10)
        slider_x = self.slider_rect.x + int((self.pen_radius / 20) * self.slider_rect.width)
        pygame.draw.circle(self.screen, WHITE, (slider_x, self.slider_rect.y + self.slider_rect.height // 2), 10)
        if self.mouseDown and self.slider_rect.collidepoint(self.mouse_pos):
            self.pen_radius = max(1, min(20, int(((self.mouse_pos[0] - self.slider_rect.x) / self.slider_rect.width) * 20)))

    def draw_tools(self):
        pygame.draw.rect(self.screen, BLACK, self.tools_rect, 2, border_radius=10)
        self.eraser_button.draw(self.screen)
        self.clear_button.draw(self.screen)

    def draw_timer(self):
        remaining_time = max(0, self.time_limit - int(time.time() - self.start_time))
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        timer_text = timer_font.render(f"{minutes:02}:{seconds:02}", True, BLACK)
        self.screen.blit(timer_text, (self.timer_rect.x + 10, self.timer_rect.y + 10))

    def draw_clear_confirmation(self):
        pygame.draw.rect(self.screen, LIGHT_GREY, (WIDTH//2 - 150, HEIGHT//2 - 50, 300, 150), border_radius=10)
        confirm_text = info_font.render("Effacer le dessin ?", True, BLACK)
        self.screen.blit(confirm_text, (WIDTH//2 - 100, HEIGHT//2 - 30))
        self.cancel_clear_button.draw(self.screen)
        self.confirm_clear_button.draw(self.screen)

    def run(self):
        running = True
        while running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

# Exemple d'utilisation
if __name__ == "__main__":
    game = DrawingPage("model.png", "Chat mignon", PURPLE)
    game.run()
