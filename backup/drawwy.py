import play
import tools
import json
import yaml
import pygame
import sys
import random
import math
import SoloGame.Ui_histoire as Ui_histoire
from datetime import datetime

if sys.platform.startswith("win"):
    import pygetwindow as gw

with open("assets/config.yaml", "r") as f:
    config = yaml.safe_load(f)

with open("assets/players_data.json") as f:
    player_data = json.load(f)

pygame.init()
W, H = tools.get_screen_size()
screen = pygame.display.set_mode((W, H))
pygame.display.set_icon(pygame.image.load("assets/icon.png"))
pygame.display.set_caption("Drawwy")

try:gw.getWindowsWithTitle("Drawwy")[0].activate()  # First plan
except:pass

# Palette de couleurs améliorée
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (170, 170, 170)
LIGHT_GRAY = (200, 200, 200)
LIGHT_BLUE = (119, 181, 254)
DARK_BLUE = (65, 105, 225)
ORANGE = (255, 95, 31)
SOFT_ORANGE = (255, 160, 122)
BEIGE = (245, 222, 179)
DARK_BEIGE = (222, 184, 135)
PASTEL_PINK = (255, 209, 220)
PASTEL_GREEN = (193, 225, 193)
PASTEL_YELLOW = (253, 253, 150)
RED = (200, 50, 50)
GREEN = (50, 200, 50)

# Police personnalisée
TITLE_FONT = pygame.font.Font(None, 300)
BUTTON_FONT = pygame.font.Font(None, 80)
MEDIUM_FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font( pygame.font.match_font("segoeuisymbol" if sys.platform.startswith("win") else "dejavusans"), 26)
VERY_SMALL_FONT = pygame.font.Font(None, 25)

# Classe pour les effets de particules
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-1, 1)
        self.speed_y = random.uniform(-3, -1)
        self.lifetime = random.randint(30, 90)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size = max(0, self.size - 0.05)
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# Classe pour les éléments de dessin décoratifs
class DrawingElement:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(["flower", "star", "heart", "cloud"])
        self.color = random.choice([(255, 102, 102), (255, 204, 102), (102, 204, 255), (153, 255, 153), (255, 153, 255)])
        self.size = random.randint(20, 50)
        self.title_scale = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.3, 0.5)  
        self.title_scale_change = random.uniform(-0.01, 0.01)
        # Store initial parameters for smooth drawing
        self.initial_title_scale = self.title_scale
        
    def update(self):
        self.title_scale += self.title_scale_change  
        self.x += math.sin(self.title_scale) * self.speed
        self.y += math.cos(self.title_scale) * self.speed
        
    def draw(self, surface):
        if self.type == "flower":
            self.draw_flower(surface)
        elif self.type == "star":
            self.draw_star(surface)
        elif self.type == "heart":
            self.draw_heart(surface)
        elif self.type == "cloud":
            self.draw_cloud(surface)
            
    def draw_flower(self, surface):
        center = (int(self.x), int(self.y))
        petal_distance = self.size // 2.5
        # Remove random trembling by using fixed title_scales
        for title_scale in range(0, 360, 72):
            rad = math.radians(title_scale)
            petal_x = center[0] + int(math.cos(rad) * petal_distance)
            petal_y = center[1] + int(math.sin(rad) * petal_distance)
            pygame.draw.circle(surface, self.color, (petal_x, petal_y), self.size // 3)
            pygame.draw.circle(surface, (0, 0, 0), (petal_x, petal_y), self.size // 3, 2)  
        pygame.draw.circle(surface, (255, 255, 0), center, self.size // 4)  
        pygame.draw.circle(surface, (0, 0, 0), center, self.size // 4, 2)  
        
    def draw_star(self, surface):
        points = []
        # Remove random trembling by using fixed title_scales
        for i in range(10):
            title_scale = math.pi / 5 * i
            radius = self.size if i % 2 == 0 else self.size // 2
            x = self.x + math.cos(title_scale) * radius
            y = self.y + math.sin(title_scale) * radius
            points.append((x, y))
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 3)  
        
    def draw_heart(self, surface):
        """Improved heart shape with smoother curves"""
        # Heart shape parameters
        size = self.size
        # Create a list of points for the heart shape
        points = []
        for title_scale in range(0, 360, 5):
            rad = math.radians(title_scale)
            # Heart parametric equations for smoother shape
            x = self.x + 16 * size/40 * math.sin(rad) ** 3
            y = self.y - (13 * size/40 * math.cos(rad) - 5 * size/40 * math.cos(2*rad) - 
                          2 * size/40 * math.cos(3*rad) - size/40 * math.cos(4*rad))
            points.append((x, y))
            
        # Fill heart shape
        pygame.draw.polygon(surface, self.color, points)
        # Draw outline
        pygame.draw.polygon(surface, (0, 0, 0), points, 2)
        
    def draw_cloud(self, surface):
        """Improved cloud with smoother shape and better organization"""
        # Cloud base parameters
        cloud_radius = self.size // 2.5
        small_radius = cloud_radius * 0.8
        
        # Main cloud body (larger central circle)
        center = (int(self.x), int(self.y))
        pygame.draw.circle(surface, self.color, center, cloud_radius)
        
        # Additional circles to form cloud shape
        offsets = [
            (-cloud_radius*0.8, -cloud_radius*0.3),  # top left
            (cloud_radius*0.8, -cloud_radius*0.3),   # top right
            (-cloud_radius*1.2, cloud_radius*0.2),   # middle left
            (cloud_radius*1.2, cloud_radius*0.2),    # middle right
            (0, -cloud_radius*0.7),                  # top middle
        ]
        
        # Draw additional circles
        for offset in offsets:
            pos = (int(center[0] + offset[0]), int(center[1] + offset[1]))
            pygame.draw.circle(surface, self.color, pos, small_radius)
        
        # Draw outline to join all circles together
        outline_points = []
        steps = 36
        for i in range(steps):
            title_scale = 2 * math.pi * i / steps
            
            # Find furthest point at this title_scale
            max_dist = cloud_radius
            max_x, max_y = center[0] + math.cos(title_scale) * cloud_radius, center[1] + math.sin(title_scale) * cloud_radius
            
            for offset in offsets:
                pos = (center[0] + offset[0], center[1] + offset[1])
                # Distance from this circle edge to center
                edge_x = pos[0] + math.cos(title_scale) * small_radius
                edge_y = pos[1] + math.sin(title_scale) * small_radius
                
                # Distance from center of main cloud
                dist_from_center = math.sqrt((edge_x - center[0])**2 + (edge_y - center[1])**2)
                
                if dist_from_center > max_dist:
                    max_dist = dist_from_center
                    max_x, max_y = edge_x, edge_y
            
            outline_points.append((max_x, max_y))
            
        # Draw cloud outline
        pygame.draw.polygon(surface, self.color, outline_points)
        pygame.draw.polygon(surface, (0, 0, 0), outline_points, 2)

# Classe pour la gestion de l'avatar
class AvatarManager:
    def __init__(self, screen):
        self.screen = screen
        self.avatar_size = 100
        self.input_text = player_data["pseudo"]
        
        # Charger ou créer l'avatar
        self.avatar_path = "assets/avatar.bmp"
        try:
            self.avatar_original = pygame.image.load(self.avatar_path).convert_alpha()
            self.avatar_original = pygame.transform.scale(self.avatar_original, (100, 100))
        except:
            # Créer un avatar par défaut
            self.avatar_original = pygame.Surface((100, 100), pygame.SRCALPHA)
            self.avatar_original.fill((100, 100, 255, 255))  # Bleu par défaut
            pygame.draw.circle(self.avatar_original, ORANGE, (50, 50), 50)
            
        self.avatar = self.avatar_original.copy()
        
        # Historique des modifications
        self.history = [self.avatar.copy()]
        self.REDo_stack = []
        
        # Positions
        self.avatar_start_pos = (W - self.avatar_size - 25, 20)
        self.pseudo_start_pos = (W - self.avatar_size - 35, self.avatar_size + 30)
        
        # Positions cibles pour l'édition
        self.avatar_target_size = int(0.71 * H)
        self.avatar_target_pos = ((W - self.avatar_target_size) // 2, (H - self.avatar_target_size) // 2-70)
        self.pseudo_target_pos = (W // 2 - 50, self.avatar_target_pos[1] + self.avatar_target_size + 25)
        self.avatar_target_size_ratio=self.avatar_target_size/self.avatar.get_size()[0]
        
        # État d'animation
        self.anim_progress = 0
        self.is_expanding = False
        self.is_retracting = False
        self.pseudo_editable = False
        self.show_buttons = False
        
        # Propriétés du pinceau
        self.drawing = False
        self.brush_size = 5
        self.size_min = 5
        self.size_max = 40
        
        # Palette de couleurs pour l'édition d'avatar
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
                       (255, 165, 0), (255, 255, 255), (0, 0, 0)]
        self.brush_color = self.colors[0]
        
        # Créer les recttitle_scales pour la palette de couleurs
        self.color_rects = [pygame.Rect(self.avatar_target_pos[0] + i * 60, 
                            self.avatar_target_pos[1] - 70, 50, 50) 
                            for i in range(len(self.colors))]
        
        # Boutons
        button_width, button_height = 160, 50
        self.cancel_button_rect = pygame.Rect(W // 2 - 150, self.pseudo_target_pos[1] + 45, 
                                             button_width, button_height)
        self.validate_button_rect = pygame.Rect(W // 2 + 30, self.pseudo_target_pos[1] + 45, 
                                               button_width, button_height)
        
        # Boutons de taille de pinceau
        size_button_width = 60
        size_button_height = 50
        self.decrease_button_rect = pygame.Rect(self.avatar_target_pos[0] + self.avatar_target_size - size_button_width, 
                                              self.avatar_start_pos[1] + size_button_height // 2 - 10, 
                                              size_button_width, size_button_height)
        self.increase_button_rect = pygame.Rect(self.avatar_target_pos[0] + self.avatar_target_size - size_button_width + 70, 
                                              self.avatar_start_pos[1] + size_button_height // 2 - 10, 
                                              size_button_width, size_button_height)
        
    def save_state(self):
        self.history.append(self.avatar.copy())
        if len(self.history) > 20:  # Limite historique
            self.history.pop(0)
        self.REDo_stack.clear()  # Reset REDo
        
    def size_button(self, rect, text, hover):
        # Ombre
        offset = 3
        pygame.draw.rect(self.screen, DARK_BEIGE if not hover else GRAY,
                       (rect.x + offset, rect.y + offset, rect.width, rect.height),
                       border_radius=30)

        # Bouton principal
        button_color = ORANGE if not hover else SOFT_ORANGE
        pygame.draw.rect(self.screen, button_color, rect, border_radius=30)

        # Texte du bouton
        text_surface = SMALL_FONT.render(text, True, BLACK)
        text_x = rect.x + (rect.width - text_surface.get_width()) // 2
        text_y = rect.y + (rect.height - text_surface.get_height()) // 2 - (2 if hover else 0)
        self.screen.blit(text_surface, (text_x, text_y))
        
    def handle_event(self, event, mouse_pos, mouse_pressed):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.show_buttons:  # Si pas déjà en mode édition
                if self.avatar_start_pos[0] < mouse_pos[0] < self.avatar_start_pos[0] + self.avatar_size and \
                   self.avatar_start_pos[1] < mouse_pos[1] < self.avatar_start_pos[1] + self.avatar_size:
                    self.input_text = player_data["pseudo"]
                    self.is_expanding = True
                    self.pseudo_editable = True
                    return True
            else:
                if self.decrease_button_rect.collidepoint(mouse_pos):
                    self.brush_size = max(self.size_min, self.brush_size - 5)
                    return True

                elif self.increase_button_rect.collidepoint(mouse_pos):
                    self.brush_size = min(self.size_max, self.brush_size + 5)
                    return True

                elif self.validate_button_rect.collidepoint(mouse_pos):  # Valider
                    pygame.image.save(self.avatar, self.avatar_path)
                    player_data["pseudo"] = self.input_text
                    self.show_buttons = False
                    self.pseudo_editable = False
                    self.is_retracting = True
                    with open("assets/players_data.json", "w") as f:
                        json.dump(player_data, f)

                    return True

                elif self.cancel_button_rect.collidepoint(mouse_pos) and self.input_text!="":  # Annuler
                    self.avatar = self.avatar_original.copy()
                    self.is_retracting = True
                    self.show_buttons = False
                    return True

                # Sélection de couleur
                for i, rect in enumerate(self.color_rects):
                    if rect.collidepoint(mouse_pos):
                        self.brush_color = self.colors[i]
                        return True
                        
                # Vérifier si on dessine sur l'avatar
                avatar_pos = self.get_current_avatar_position()
                avatar_size = self.get_current_avatar_size()
                
                rel_x = (mouse_pos[0] - avatar_pos[0]) / avatar_size
                rel_y = (mouse_pos[1] - avatar_pos[1]) / avatar_size
                if 0 <= rel_x <= 1 and 0 <= rel_y <= 1:
                    px = int(rel_x * self.avatar.get_width())
                    py = int(rel_y * self.avatar.get_height())
                    pygame.draw.circle(self.avatar, self.brush_color, (px, py), self.brush_size//self.avatar_target_size_ratio)
                    return True
                
        elif event.type == pygame.MOUSEBUTTONUP and self.show_buttons:
            self.save_state()
            return True
            
        elif event.type == pygame.KEYDOWN and self.pseudo_editable:
            if event.key == pygame.K_RETURN:  # Valider avec ENTER
                pygame.image.save(self.avatar, self.avatar_path)
                player_data["pseudo"] = self.input_text
                self.show_buttons = False
                self.pseudo_editable = False
                self.is_retracting = True
                with open("assets/players_data.json", "w") as f:
                    json.dump(player_data, f)
                return True
            elif event.key == pygame.K_ESCAPE and self.input_text!="":  # Annuler avec ESC
                self.avatar = self.avatar_original.copy()
                self.is_retracting = True
                self.show_buttons = False
                return True
            elif event.key == pygame.K_UP:
                self.brush_size = min(self.size_max, self.brush_size + 5)
                return True
            elif event.key == pygame.K_DOWN:
                self.brush_size = max(self.size_max, self.brush_size - 5)
                return True
            elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Z (Undo)
                if len(self.history) > 1:
                    self.REDo_stack.append(self.history.pop())
                    self.avatar = self.history[-1].copy()
                return True
            elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:  # Ctrl+Y (REDo)
                if self.REDo_stack:
                    self.avatar = self.REDo_stack.pop()
                    self.history.append(self.avatar.copy())
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            elif event.unicode:
                self.input_text += event.unicode
                return True
                
        return False  # L'événement n'a pas été géré
        
    def update(self, mouse_pos, mouse_pressed):
        # Dessin sur l'avatar si en mode édition et que la souris est appuyée
        if self.show_buttons and True in mouse_pressed:
            avatar_pos = self.get_current_avatar_position()
            avatar_size = self.get_current_avatar_size()
            
            rel_x = (mouse_pos[0] - avatar_pos[0]) / avatar_size
            rel_y = (mouse_pos[1] - avatar_pos[1]) / avatar_size
            if 0 <= rel_x <= 1 and 0 <= rel_y <= 1:
                px = int(rel_x * self.avatar.get_width())
                py = int(rel_y * self.avatar.get_height())
                pygame.draw.circle(self.avatar, self.brush_color, (px, py), max(1,self.brush_size/self.avatar_target_size_ratio))
        
        # Animation Expansion
        if self.is_expanding:
            self.anim_progress += 0.1
            if self.anim_progress >= 1:
                self.anim_progress = 1
                self.is_expanding = False
                self.show_buttons = True
                self.pseudo_editable = True
                
        # Animation Retrait
        if self.is_retracting:
            self.anim_progress -= 0.1
            if self.anim_progress <= 0:
                self.anim_progress = 0
                self.is_retracting = False
                self.pseudo_editable = False
    
    def get_current_avatar_position(self):
        return (
            int(self.avatar_start_pos[0] + (self.avatar_target_pos[0] - self.avatar_start_pos[0]) * self.anim_progress),
            int(self.avatar_start_pos[1] + (self.avatar_target_pos[1] - self.avatar_start_pos[1]) * self.anim_progress)
        )
        
    def get_current_avatar_size(self):
        return int(100 + (self.avatar_target_size - 100) * self.anim_progress)
        
    def get_current_pseudo_position(self):
        return (
            int(self.pseudo_start_pos[0] + (self.pseudo_target_pos[0] - self.pseudo_start_pos[0]) * self.anim_progress),
            int(self.pseudo_start_pos[1] + (self.pseudo_target_pos[1] - self.pseudo_start_pos[1]) * self.anim_progress)
        )
    
    def draw(self):
        # Dessiner l'avatar
        avatar_pos = self.get_current_avatar_position()
        avatar_size = self.get_current_avatar_size()
        pseudo_pos = self.get_current_pseudo_position()
        
        # Contour ORANGE de l'avatar
        pygame.draw.circle(self.screen, ORANGE, 
                          (avatar_pos[0] + avatar_size // 2, avatar_pos[1] + avatar_size // 2), 
                          avatar_size // 2 + 4 + (8 * self.anim_progress))
        
        # Afficher l'avatar avec masque circulaire
        temp_avatar = pygame.transform.scale(self.avatar, (avatar_size, avatar_size))
        tools.apply_circular_mask(temp_avatar)
        self.screen.blit(temp_avatar, avatar_pos)
        
        # Afficher le pseudo
        pseudo_surf = MEDIUM_FONT.render(self.input_text + "|" if self.pseudo_editable else player_data["pseudo"], True, WHITE)
        self.screen.blit(pseudo_surf, pseudo_pos)
        
        # Afficher les boutons et contrôles d'édition si activés
        if self.show_buttons:
            # Palette de couleurs
            for i, rect in enumerate(self.color_rects):
                pygame.draw.rect(self.screen, self.colors[i], rect, border_radius=8)
                
            # Aperçu de la taille du pinceau
            pygame.draw.circle(self.screen, self.brush_color, 
                              (self.avatar_target_pos[0] + self.avatar_target_size + 5, 
                               self.avatar_start_pos[1] + 50 + 60), 
                              self.brush_size + 5, width=5)
            
            # Boutons de taille du pinceau
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            for rect, label in [(self.increase_button_rect, "+"), (self.decrease_button_rect, "-")]:
                hover = rect.collidepoint(mouse_x, mouse_y)
                self.size_button(rect, label, hover)
            
            # Boutons valider/annuler
            pygame.draw.rect(self.screen, GREEN, self.validate_button_rect, border_radius=10)
            pygame.draw.rect(self.screen, RED, self.cancel_button_rect, border_radius=10)
            
            validate_text = SMALL_FONT.render("✔ Valider", True, WHITE)
            cancel_text = SMALL_FONT.render("✕ Annuler", True, WHITE)
            
            self.screen.blit(validate_text, (self.validate_button_rect.x + 20, self.validate_button_rect.y + 10))
            self.screen.blit(cancel_text, (self.cancel_button_rect.x + 20, self.cancel_button_rect.y + 10))
            
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_textbox(text, x, y, width, height, font, text_color, bg_color, surface, border_radius=10):
    # Dessiner la boîte
    box_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, bg_color, box_rect, border_radius=border_radius)
    
    # Dessiner le texte
    draw_text(text, font, text_color, surface, x + width // 2, y + height // 2)
    
    return box_rect

# Créer quelques éléments de dessin flottants
drawing_elements = [DrawingElement(random.randint(0, W), random.randint(0, H)) for _ in range(50)]

# Liste pour stocker les particules
particles = []

# Paramètres d'animation
animation_counter = 0
title_angle = 0

connected=tools.is_connected()
last_sec_check_connection=datetime.now().second

# État du jeu
current_page = "menu"
# Créer le gestionnaire d'avatar
avatar_manager = AvatarManager(screen)

clock = pygame.time.Clock()
running = True

while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False

    if datetime.now().second==(last_sec_check_connection+2)%60:
        last_sec_check_connection=datetime.now().second
        connected=tools.is_connected()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_click = True
            
        # Donner priorité aux événements d'avatar s'il est en cours d'édition
        if avatar_manager.handle_event(event, mouse_pos, pygame.mouse.get_pressed()):
            continue  # Événement déjà traité par le gestionnaire d'avatar
    
    # Mise à jour de l'animation
    animation_counter += 1
    title_angle += 0.02
    
    # Mise à jour des éléments d'arrière plan
    for element in drawing_elements:
        element.update()
    
    # Mise à jour des particules
    for particle in particles[:]:
        particle.update()
        if particle.lifetime <= 0:
            particles.remove(particle)
    
    # Ajouter de nouvelles particules occasionnellement
    if animation_counter % 5 == 0 and len(particles) < 200:
        particles.append(Particle(
            random.randint(0, W),
            H + 10,
            random.choice([SOFT_ORANGE, PASTEL_PINK, PASTEL_GREEN, PASTEL_YELLOW])
        ))
    
    # Mise à jour du gestionnaire d'avatar
    avatar_manager.update(mouse_pos, pygame.mouse.get_pressed())
    
    # Fond
    screen.fill(LIGHT_BLUE)
    
    # Dessiner les éléments de dessin en arrière-plan
    for element in drawing_elements:
        element.draw(screen)
    
    # Dessiner les particules
    for particle in particles:
        particle.draw(screen)
    
    # === ÉCRAN DU MENU PRINCIPAL ===
    if current_page == "menu":
        avatar_manager.draw()
        
        if not (avatar_manager.show_buttons or avatar_manager.is_expanding or avatar_manager.is_retracting):
            # Panneau principal (effet papier)
            main_panel_width = 900
            main_panel_height = 750
            main_panel_x = (W - main_panel_width) // 2
            main_panel_y = (H - main_panel_height) // 2
            
            # Ombre du panneau
            pygame.draw.rect(screen, DARK_BEIGE, 
                            (main_panel_x + 15, main_panel_y + 15, 
                            main_panel_width, main_panel_height), 
                            border_radius=40)
            
            # Panneau principal
            pygame.draw.rect(screen, BEIGE, 
                            (main_panel_x, main_panel_y, 
                            main_panel_width, main_panel_height), 
                            border_radius=40)
            
            # Texture du papier (points aléatoires)
            for _ in range(500):
                px = random.randint(main_panel_x, main_panel_x + main_panel_width)
                py = random.randint(main_panel_y, main_panel_y + main_panel_height)
                if (px - main_panel_x - main_panel_width//2)**2 + (py - main_panel_y - main_panel_height//2)**2 <= (main_panel_width//2)**2:
                    color_variation = random.randint(-15, 5)
                    point_color = (
                        min(255, max(0, BEIGE[0] + color_variation)),
                        min(255, max(0, BEIGE[1] + color_variation)),
                        min(255, max(0, BEIGE[2] + color_variation))
                    )
                    pygame.draw.circle(screen, point_color, (px, py), 1)
            
            # Titre avec effet d'animation
            title_scale = 1.0 + 0.05 * math.sin(title_angle * 2)
            title_size = int(280 * title_scale)
            TITLE_FONT_animated = pygame.font.SysFont(None, title_size)
            
            # Ombre du titre
            draw_text("DRAWWY", TITLE_FONT_animated, GRAY, screen, 
                    W // 2 + 8, main_panel_y + 150 + 8)
            
            # Titre
            draw_text("DRAWWY", TITLE_FONT_animated, BLACK, screen, 
                    W // 2, main_panel_y + 150)
            
            
            # Boutons
            buttons = ["JOUER", "SUCCÈS", "QUITTER"]
            button_width = 500
            button_height = 80
            button_x = (W - button_width) // 2
            button_y_start = main_panel_y + 320
            buttons_offsets=5
            for i, button_text in enumerate(buttons):
                button_y = button_y_start + i * 1.3 * button_height
                
                # Animation de survol
                hover = button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height
                
                
                # Dessiner l'ombre du bouton
                pygame.draw.rect(screen, DARK_BEIGE if not hover else GRAY, 
                            (button_x + buttons_offsets, button_y + buttons_offsets, button_width, button_height), 
                            border_radius=40)
                
                # Dessiner le bouton
                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                pygame.draw.rect(screen, 
                                SOFT_ORANGE if hover else ORANGE, 
                                button_rect, 
                                border_radius=40)
                

                # Texte du bouton avec un léger déplacement lorsqu'il est survolé
                text_y_offset = 3 if hover else 0
                draw_text(button_text, BUTTON_FONT, BLACK, screen, 
                        button_x + button_width // 2, 
                        button_y + button_height // 2 - text_y_offset)
                
                # Gestion des clics
                if mouse_click and hover:
                    for _ in range(20):
                        particles.append(Particle(
                            random.randint(button_x, button_x + button_width),
                            button_y + button_height // 2,
                            random.choice([ORANGE, SOFT_ORANGE, PASTEL_YELLOW])
                        ))
                    
                    if button_text == "QUITTER":
                        running = False
                    elif button_text == "JOUER":
                        current_page = "play"
                    elif button_text == "SUCCÈS":
                        current_page = "achievements"

                # Crédits

                # Dessiner le bouton rond "crédit"
                credit_button_radius = 50
                credit_button_x = main_panel_x + main_panel_width - credit_button_radius - 10
                credit_button_y = main_panel_y + main_panel_height- credit_button_radius - 10
                buttons_offsets=4
                
                # Animation de survol du credit
                hover_credit = math.sqrt((mouse_pos[0] - credit_button_x)**2 + (mouse_pos[1] - credit_button_y)**2) <= credit_button_radius
                # Dessiner le cercle
                pygame.draw.circle(screen, 
                                DARK_BEIGE if not hover_credit else GRAY, 
                                (credit_button_x + buttons_offsets-1, credit_button_y + buttons_offsets), 
                                credit_button_radius)
                pygame.draw.circle(screen, 
                                SOFT_ORANGE if hover_credit else ORANGE,
                                (credit_button_x, credit_button_y),
                                credit_button_radius)

                # Texte du bouton CREDit avec un léger déplacement lorsqu'il est survolé
                credit_text_y_offset = 3 if hover_credit else 0
                draw_text("CRÉDIT", VERY_SMALL_FONT, BLACK, screen, 
                        credit_button_x, 
                        credit_button_y - credit_text_y_offset)
                

            # Effets de particules lors du clic
            if mouse_click:
                for _ in range(20):
                    particles.append(Particle(
                        random.randint(mouse_pos[0]-30, mouse_pos[0]+30),
                        random.randint(mouse_pos[1]-30, mouse_pos[1]+30),
                        random.choice([ORANGE, SOFT_ORANGE, PASTEL_YELLOW])
                    ))

    

    # === ÉCRAN DE JEU ===
    elif current_page == "play":
        # Titre
        draw_text("Mode de jeu", BUTTON_FONT, BLACK, screen, W // 2, 100)
        
        # Options de jeu
        game_modes = ["Solo", "Multijoueur"]
        mode_width = 300
        mode_height = 200
        modes_y = H // 2 - mode_height // 2
        
        total_width = len(game_modes) * mode_width + (len(game_modes) - 1) * 50
        start_x = (W - total_width) // 2
        
        for i, mode in enumerate(game_modes):
            mode_x = start_x + i * (mode_width + 50)
            mode_rect = pygame.Rect(mode_x, modes_y, mode_width, mode_height)
            
            # Vérifier si la souris survole
            hover = mode_rect.collidepoint(mouse_pos) and (mode=="Solo" or connected)
            
            # Dessiner l'ombre
            pygame.draw.rect(screen, DARK_BEIGE, 
                            (mode_x + 10, modes_y + 10, mode_width, mode_height), 
                            border_radius=20)
            
            # Dessiner le fond
            color = SOFT_ORANGE if hover else BEIGE
            pygame.draw.rect(screen, color, mode_rect, border_radius=20)
            
            # Dessiner le texte
            draw_text(mode, SMALL_FONT, BLACK if mode=="Solo" or connected else RED, screen, 
                     mode_x + mode_width // 2, modes_y + mode_height // 2)
            
            # Gérer le clic
            if mouse_click and hover:
                if mode=="Solo":
                    Ui_histoire.SoloGame(screen,clock, W,H)
                    current_page = "menu"
                elif mode=="Multijoueur" and tools.is_connected():
                    play.MultiplayersGame(screen,clock, W,H)
                    current_page = "menu"
        
        # Bouton de retour
        back_button_rect = draw_textbox("RETOUR", W // 2 - 100, H - 100, 
                                      200, 50, SMALL_FONT, BLACK, ORANGE, screen, 25)
        
        if mouse_click and back_button_rect.collidepoint(mouse_pos):
            current_page = "menu"
    
    # === ÉCRAN DES SUCCÈS ===
    elif current_page == "achievements":
        # Titre
        draw_text("SUCCÈS", BUTTON_FONT, BLACK, screen, W // 2, 100)
        
        # Panneau principal
        main_panel_width = 800
        main_panel_height = 500
        main_panel_x = (W - main_panel_width) // 2
        main_panel_y = 180
        
        pygame.draw.rect(screen, DARK_BEIGE, 
                        (main_panel_x + 10, main_panel_y + 10, 
                         main_panel_width, main_panel_height), 
                        border_radius=30)
        
        pygame.draw.rect(screen, BEIGE, 
                        (main_panel_x, main_panel_y, 
                         main_panel_width, main_panel_height), 
                        border_radius=30)
        
        # Liste de succès fictifs
        achievements = [
            {"name": "Premier dessin", "description": "Complétez votre premier dessin", "completed": True},
            {"name": "Artiste en herbe", "description": "Dessinez 10 dessins", "completed": True},
            {"name": "Maître du crayon", "description": "Dessinez 50 dessins", "completed": False},
            {"name": "Collaborateur", "description": "Jouez en multijoueur 5 fois", "completed": False},
            {"name": "Perfectionniste", "description": "Obtenez un score parfait", "completed": False}
        ]
        
        achievement_y = main_panel_y + 60
        achievement_height = 70
        
        for achievement in achievements:
            # Fond
            color = PASTEL_GREEN if achievement["completed"] else LIGHT_GRAY
            pygame.draw.rect(screen, color, 
                            (main_panel_x + 50, achievement_y, 
                             main_panel_width - 100, achievement_height), 
                            border_radius=15)
            
            # Texte
            draw_text(achievement["name"], SMALL_FONT, BLACK, screen, 
                     main_panel_x + 400, achievement_y + 20)
            
            description_font = pygame.font.SysFont(None, 30)
            draw_text(achievement["description"], description_font, GRAY, screen, 
                     main_panel_x + 400, achievement_y + 50)
            
            # Icône
            if achievement["completed"]:
                pygame.draw.circle(screen, DARK_BLUE, 
                                  (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                  20)
                pygame.draw.line(screen, WHITE, 
                                (main_panel_x + 90, achievement_y + achievement_height // 2), 
                                (main_panel_x + 100, achievement_y + achievement_height // 2 + 10), 
                                4)
                pygame.draw.line(screen, WHITE, 
                                (main_panel_x + 100, achievement_y + achievement_height // 2 + 10), 
                                (main_panel_x + 115, achievement_y + achievement_height // 2 - 10), 
                                4)
            else:
                pygame.draw.circle(screen, GRAY, 
                                  (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                  20)
                pygame.draw.circle(screen, color, 
                                  (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                  16)
            
            achievement_y += achievement_height + 10
        
        # Bouton de retour
        back_button_rect = draw_textbox("RETOUR", W // 2 - 100, H - 100, 
                                      200, 50, SMALL_FONT, BLACK, ORANGE, screen, 25)
        
        if mouse_click and back_button_rect.collidepoint(mouse_pos):
            current_page = "menu"
        
    
    # Afficher la version
    version_text = "DRAWWY v1.0"
    version_font = pygame.font.SysFont(None, 24)
    text_surface = version_font.render(version_text, True, BLACK)
    screen.blit(text_surface, (20, H - 30))
    
    pygame.display.flip()
    clock.tick(config["game_page_fps"])

pygame.quit()
sys.exit()