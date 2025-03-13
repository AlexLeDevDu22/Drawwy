import pygame
import sys
import random
import math

pygame.init()
info_ecran = pygame.display.Info()
largeur, hauteur = info_ecran.current_w, info_ecran.current_h
ecran = pygame.display.set_mode((largeur, hauteur))
pygame.display.set_caption("DRAWWY")

# Palette de couleurs améliorée
white = (255, 255, 255)
black = (0, 0, 0)
gray = (170, 170, 170)
light_blue = (119, 181, 254)
dark_blue = (65, 105, 225)
light_gray = (200, 200, 200)
orange = (255, 95, 31)
soft_orange = (255, 160, 122)
beige = (245, 222, 179)
dark_beige = (222, 184, 135)
pastel_pink = (255, 209, 220)
pastel_green = (193, 225, 193)
pastel_yellow = (253, 253, 150)

# Police personnalisée
try:
    title_font = pygame.font.Font(None, 300)
    button_font = pygame.font.Font(None, 80)
    small_font = pygame.font.Font(None, 40)
except:
    title_font = pygame.font.SysFont(None, 300)
    button_font = pygame.font.SysFont(None, 80)
    small_font = pygame.font.SysFont(None, 40)

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
import pygame
import random
import math

import pygame
import random
import math

class DrawingElement:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(["flower", "star", "heart", "cloud"])
        self.color = random.choice([(255, 102, 102), (255, 204, 102), (102, 204, 255), (153, 255, 153), (255, 153, 255)])
        self.size = random.randint(20, 50)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.3, 0.5)  
        self.angle_change = random.uniform(-0.01, 0.01)
        # Store initial parameters for smooth drawing
        self.initial_angle = self.angle
        
    def update(self):
        self.angle += self.angle_change  
        self.x += math.sin(self.angle) * self.speed
        self.y += math.cos(self.angle) * self.speed
        
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
        # Remove random trembling by using fixed angles
        for angle in range(0, 360, 72):
            rad = math.radians(angle)
            petal_x = center[0] + int(math.cos(rad) * petal_distance)
            petal_y = center[1] + int(math.sin(rad) * petal_distance)
            pygame.draw.circle(surface, self.color, (petal_x, petal_y), self.size // 3)
            pygame.draw.circle(surface, (0, 0, 0), (petal_x, petal_y), self.size // 3, 2)  
        pygame.draw.circle(surface, (255, 255, 0), center, self.size // 4)  
        pygame.draw.circle(surface, (0, 0, 0), center, self.size // 4, 2)  
        
    def draw_star(self, surface):
        points = []
        # Remove random trembling by using fixed angles
        for i in range(10):
            angle = math.pi / 5 * i
            radius = self.size if i % 2 == 0 else self.size // 2
            x = self.x + math.cos(angle) * radius
            y = self.y + math.sin(angle) * radius
            points.append((x, y))
        pygame.draw.polygon(surface, self.color, points)
        pygame.draw.polygon(surface, (0, 0, 0), points, 3)  
        
    def draw_heart(self, surface):
        """Improved heart shape with smoother curves"""
        # Heart shape parameters
        size = self.size
        # Create a list of points for the heart shape
        points = []
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
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
            angle = 2 * math.pi * i / steps
            
            # Find furthest point at this angle
            max_dist = cloud_radius
            max_x, max_y = center[0] + math.cos(angle) * cloud_radius, center[1] + math.sin(angle) * cloud_radius
            
            for offset in offsets:
                pos = (center[0] + offset[0], center[1] + offset[1])
                # Distance from this circle edge to center
                edge_x = pos[0] + math.cos(angle) * small_radius
                edge_y = pos[1] + math.sin(angle) * small_radius
                
                # Distance from center of main cloud
                dist_from_center = math.sqrt((edge_x - center[0])**2 + (edge_y - center[1])**2)
                
                if dist_from_center > max_dist:
                    max_dist = dist_from_center
                    max_x, max_y = edge_x, edge_y
            
            outline_points.append((max_x, max_y))
            
        # Draw cloud outline
        pygame.draw.polygon(surface, self.color, outline_points)
        pygame.draw.polygon(surface, (0, 0, 0), outline_points, 2)
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
drawing_elements = [DrawingElement(random.randint(0, largeur), random.randint(0, hauteur)) for _ in range(50)]

# Liste pour stocker les particules
particles = []

# Paramètres d'animation
animation_counter = 0
angle = 0

# État du jeu
current_screen = "menu"
selected_button = None
active_buttons = []

# Musique et son
try:
    pygame.mixer.init()
    button_sound = pygame.mixer.Sound("button_click.wav")  # Remplacer par le chemin vers un son si disponible
    has_sound = True
except:
    has_sound = False

clock = pygame.time.Clock()
running = True



while running:
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_clicked = True
    
    # Mise à jour de l'animation
    animation_counter += 1
    angle += 0.02
    
    # Mise à jour des éléments de dessin
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
            random.randint(0, largeur),
            hauteur + 10,
            random.choice([soft_orange, pastel_pink, pastel_green, pastel_yellow])
        ))
    
    # Effacer l'écran
    ecran.fill(light_blue)
    
    # Dessiner les éléments de dessin en arrière-plan
    for element in drawing_elements:
        element.draw(ecran)
    
    # Dessiner les particules
    for particle in particles:
        particle.draw(ecran)
    
    # === ÉCRAN DU MENU PRINCIPAL ===
    if current_screen == "menu":
        # Panneau principal (effet papier)
        main_panel_width = 900
        main_panel_height = 750
        main_panel_x = (largeur - main_panel_width) // 2
        main_panel_y = (hauteur - main_panel_height) // 2
        
        # Ombre du panneau
        pygame.draw.rect(ecran, dark_beige, 
                        (main_panel_x + 15, main_panel_y + 15, 
                         main_panel_width, main_panel_height), 
                        border_radius=40)
        
        # Panneau principal
        pygame.draw.rect(ecran, beige, 
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
                    min(255, max(0, beige[0] + color_variation)),
                    min(255, max(0, beige[1] + color_variation)),
                    min(255, max(0, beige[2] + color_variation))
                )
                pygame.draw.circle(ecran, point_color, (px, py), 1)
        
        # Titre avec effet d'animation
        title_scale = 1.0 + 0.05 * math.sin(angle * 2)
        title_size = int(280 * title_scale)
        title_font_animated = pygame.font.SysFont(None, title_size)
        
        # Ombre du titre
        draw_text("DRAWWY", title_font_animated, gray, ecran, 
                 largeur // 2 + 8, main_panel_y + 150 + 8)
        
        # Titre
        draw_text("DRAWWY", title_font_animated, black, ecran, 
                 largeur // 2, main_panel_y + 150)
        
        
        # Boutons
        buttons = ["JOUER", "SUCCÈS", "QUITTER"]
        button_width = 500
        button_height = 80
        button_x = (largeur - button_width) // 2
        button_y_start = main_panel_y + 320
        
        active_buttons = []
        
        for i, button_text in enumerate(buttons):
            button_y = button_y_start + i * 1.3 * button_height
            
            # Animation de survol
            hover = False
            if button_x <= mouse_pos[0] <= button_x + button_width and button_y <= mouse_pos[1] <= button_y + button_height:
                hover = True
                if selected_button != i:
                    selected_button = i
                
                # Ajouter quelques particules sur survol
                if animation_counter % 10 == 0:
                    for _ in range(3):
                        particles.append(Particle(
                            random.randint(button_x, button_x + button_width),
                            button_y + button_height,
                            random.choice([orange, soft_orange])
                        ))
            
            # Dessiner l'ombre du bouton
            offset = 5
            pygame.draw.rect(ecran, dark_beige if not hover else gray, 
                           (button_x + offset, button_y + offset, button_width, button_height), 
                           border_radius=40)
            
            # Dessiner le bouton
            button_color = orange if not hover else soft_orange
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            pygame.draw.rect(ecran, button_color, button_rect, border_radius=40)
            

            
            # Texte du bouton avec un léger déplacement lorsqu'il est survolé
            text_y_offset = 3 if hover else 0
            draw_text(button_text, button_font, black, ecran, 
                     button_x + button_width // 2, 
                     button_y + button_height // 2 - text_y_offset)
            
            active_buttons.append((button_rect, button_text))
            
            # Gestion des clics
            if mouse_clicked and hover:
                if has_sound:
                    button_sound.play()
                
                # Effets de particules lors du clic
                for _ in range(20):
                    particles.append(Particle(
                        random.randint(button_x, button_x + button_width),
                        button_y + button_height // 2,
                        random.choice([orange, soft_orange, pastel_yellow])
                    ))
                
                if button_text == "QUITTER":
                    running = False
                elif button_text == "JOUER":
                    current_screen = "play"
                elif button_text == "SUCCÈS":
                    current_screen = "achievements"
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




    # === ÉCRAN DE JEU ===
    elif current_screen == "play":
        # Titre
        draw_text("Mode de jeu", button_font, black, ecran, largeur // 2, 100)
        
        # Options de jeu
        game_modes = ["Solo", "Multijoueur",]
        mode_width = 300
        mode_height = 200
        modes_y = hauteur // 2 - mode_height // 2
        
        total_width = len(game_modes) * mode_width + (len(game_modes) - 1) * 50
        start_x = (largeur - total_width) // 2
        
        for i, mode in enumerate(game_modes):
            mode_x = start_x + i * (mode_width + 50)
            mode_rect = pygame.Rect(mode_x, modes_y, mode_width, mode_height)
            
            # Vérifier si la souris survole
            hover = mode_rect.collidepoint(mouse_pos)
            
            # Dessiner l'ombre
            pygame.draw.rect(ecran, dark_beige, 
                            (mode_x + 10, modes_y + 10, mode_width, mode_height), 
                            border_radius=20)
            
            # Dessiner le fond
            color = soft_orange if hover else beige
            pygame.draw.rect(ecran, color, mode_rect, border_radius=20)
            
            # Dessiner le texte
            draw_text(mode, small_font, black, ecran, 
                     mode_x + mode_width // 2, modes_y + mode_height // 2)
            
            # Gérer le clic
            if mouse_clicked and hover:
                if has_sound:
                    button_sound.play()
                # Logique pour chaque mode de jeu ici
        
        # Bouton de retour
        back_button_rect = draw_textbox("RETOUR", largeur // 2 - 100, hauteur - 100, 
                                      200, 50, small_font, black, orange, ecran, 25)
        
        if mouse_clicked and back_button_rect.collidepoint(mouse_pos):
            if has_sound:
                button_sound.play()
            current_screen = "menu"
    
    # === ÉCRAN DES SUCCÈS ===
    elif current_screen == "achievements":
        # Titre
        draw_text("SUCCÈS", button_font, black, ecran, largeur // 2, 100)
        
        # Panneau principal
        main_panel_width = 800
        main_panel_height = 500
        main_panel_x = (largeur - main_panel_width) // 2
        main_panel_y = 180
        
        pygame.draw.rect(ecran, dark_beige, 
                        (main_panel_x + 10, main_panel_y + 10, 
                         main_panel_width, main_panel_height), 
                        border_radius=30)
        
        pygame.draw.rect(ecran, beige, 
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
            color = pastel_green if achievement["completed"] else light_gray
            pygame.draw.rect(ecran, color, 
                            (main_panel_x + 50, achievement_y, 
                             main_panel_width - 100, achievement_height), 
                            border_radius=15)
            
            # Texte
            draw_text(achievement["name"], small_font, black, ecran, 
                     main_panel_x + 400, achievement_y + 20)
            
            description_font = pygame.font.SysFont(None, 30)
            draw_text(achievement["description"], description_font, gray, ecran, 
                     main_panel_x + 400, achievement_y + 50)
            
            # Icône
            if achievement["completed"]:
                pygame.draw.circle(ecran, dark_blue, 
                                  (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                  20)
                pygame.draw.line(ecran, white, 
                                (main_panel_x + 90, achievement_y + achievement_height // 2), 
                                (main_panel_x + 100, achievement_y + achievement_height // 2 + 10), 
                                4)
                pygame.draw.line(ecran, white, 
                                (main_panel_x + 100, achievement_y + achievement_height // 2 + 10), 
                                (main_panel_x + 115, achievement_y + achievement_height // 2 - 10), 
                                4)
            else:
                pygame.draw.circle(ecran, gray, 
                                  (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                  20)
                pygame.draw.circle(ecran, color, 
                                  (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                  16)
            
            achievement_y += achievement_height + 10
        
        # Bouton de retour
        back_button_rect = draw_textbox("RETOUR", largeur // 2 - 100, hauteur - 100, 
                                      200, 50, small_font, black, orange, ecran, 25)
        
        if mouse_clicked and back_button_rect.collidepoint(mouse_pos):
            if has_sound:
                button_sound.play()
            current_screen = "menu"
        
    
    # Afficher la version
    version_text = "DRAWWY v1.0"
    version_font = pygame.font.SysFont(None, 24)
    text_surface = version_font.render(version_text, True, black)
    ecran.blit(text_surface, (20, hauteur - 30))
    
    pygame.display.flip()
    clock.tick(60)  # Limiter à 60 FPS

pygame.quit()
sys.exit()