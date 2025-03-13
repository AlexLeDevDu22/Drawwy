import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from Menu.ui.elements import *
from shared.tools import get_screen_size
from shared.common_ui import *
from shared.common_utils import *

import pygame
import random
import math

class Menu:
    def __init__(self, screen):

        self.screen=screen
        self.W, self.H = get_screen_size

        # Créer quelques éléments de dessin flottants
        drawing_elements = [BackgroundElement(random.randint(0, self.W), random.randint(0, self.H)) for _ in range(50)]

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


        while True:
            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
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
                    random.randint(0, self.W),
                    self.H + 10,
                    random.choice([SOFT_ORANGE, PASTEL_PINK, PASTEL_GREEN, PASTEL_YELLOW])
                ))
            
            # Effacer l'écran
            self.screen.fill(LIGHT_BLUE)
            
            # Dessiner les éléments de dessin en arrière-plan
            for element in drawing_elements:
                element.draw(self.screen)
            
            # Dessiner les particules
            for particle in particles:
                particle.draw(self.screen)
            
            # === ÉCRAN DU MENU PRINCIPAL ===
            if current_screen == "menu":
                # Panneau principal (effet papier)
                main_panel_width = 900
                main_panel_height = 750
                main_panel_x = (self.W - main_panel_width) // 2
                main_panel_y = (self.H - main_panel_height) // 2
                
                # Ombre du panneau
                pygame.draw.rect(self.screen, DARK_BEIGE, 
                                (main_panel_x + 15, main_panel_y + 15, 
                                main_panel_width, main_panel_height), 
                                border_radius=40)
                
                # Panneau principal
                pygame.draw.rect(self.screen, BEIGE, 
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
                        pygame.draw.circle(self.screen, point_color, (px, py), 1)
                
                # Titre avec effet d'animation
                title_scale = 1.0 + 0.05 * math.sin(angle * 2)
                title_size = int(280 * title_scale)
                title_font_animated = pygame.font.SysFont(None, title_size)
                
                # Ombre du titre
                draw_text("DRAWWY", title_font_animated, GRAY, self.screen, 
                        self.W // 2 + 8, main_panel_y + 150 + 8)
                
                # Titre
                draw_text("DRAWWY", title_font_animated, BLACK, self.screen, 
                        self.W // 2, main_panel_y + 150)
                
                
                # Boutons
                buttons = ["JOUER", "SUCCÈS", "QUITTER"]
                button_width = 500
                button_height = 80
                button_x = (self.W - button_width) // 2
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
                                    random.choice([ORANGE, SOFT_ORANGE])
                                ))
                    
                    # Dessiner l'ombre du bouton
                    offset = 5
                    pygame.draw.rect(self.screen, DARK_BEIGE if not hover else GRAY, 
                                (button_x + offset, button_y + offset, button_width, button_height), 
                                border_radius=40)
                    
                    # Dessiner le bouton
                    button_color = ORANGE if not hover else SOFT_ORANGE
                    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                    pygame.draw.rect(self.screen, button_color, button_rect, border_radius=40)
                    

                    
                    # Texte du bouton avec un léger déplacement lorsqu'il est survolé
                    text_y_offset = 3 if hover else 0
                    draw_text(button_text, BUTTON_FONT, BLACK, self.screen, 
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
                                random.choice([ORANGE, SOFT_ORANGE, PASTEL_YELLOW])
                            ))
                        
                        if button_text == "QUITTER":
                            running = False
                        elif button_text == "JOUER":
                            current_screen = "play"
                        elif button_text == "SUCCÈS":
                            current_screen = "achievements"
            

            # === ÉCRAN DE JEU ===
            elif current_screen == "play":
                # Titre
                draw_text("Mode de jeu", BUTTON_FONT, BLACK, self.screen, self.W // 2, 100)
                
                # Options de jeu
                game_modes = ["Solo", "Multijoueur",]
                mode_width = 300
                mode_height = 200
                modes_y = self.H // 2 - mode_height // 2
                
                total_width = len(game_modes) * mode_width + (len(game_modes) - 1) * 50
                start_x = (self.W - total_width) // 2
                
                for i, mode in enumerate(game_modes):
                    mode_x = start_x + i * (mode_width + 50)
                    mode_rect = pygame.Rect(mode_x, modes_y, mode_width, mode_height)
                    
                    # Vérifier si la souris survole
                    hover = mode_rect.collidepoint(mouse_pos)
                    
                    # Dessiner l'ombre
                    pygame.draw.rect(self.screen, DARK_BEIGE, 
                                    (mode_x + 10, modes_y + 10, mode_width, mode_height), 
                                    border_radius=20)
                    
                    # Dessiner le fond
                    color = SOFT_ORANGE if hover else BEIGE
                    pygame.draw.rect(self.screen, color, mode_rect, border_radius=20)
                    
                    # Dessiner le texte
                    draw_text(mode, SMALL_FONT, BLACK, self.screen, 
                            mode_x + mode_width // 2, modes_y + mode_height // 2)
                    
                    # Gérer le clic
                    if mouse_clicked and hover:
                        if has_sound:
                            button_sound.play()
                        # Logique pour chaque mode de jeu ici
                
                # Bouton de retour
                back_button_rect = draw_textbox("RETOUR", self.W // 2 - 100, self.H - 100, 
                                            200, 50, SMALL_FONT, BLACK, ORANGE, self.screen, 25)
                
                if mouse_clicked and back_button_rect.collidepoint(mouse_pos):
                    if has_sound:
                        button_sound.play()
                    current_screen = "menu"
            
            # === ÉCRAN DES SUCCÈS ===
            elif current_screen == "achievements":
                # Titre
                draw_text("SUCCÈS", BUTTON_FONT, BLACK, self.screen, self.W // 2, 100)
                
                # Panneau principal
                main_panel_width = 800
                main_panel_height = 500
                main_panel_x = (self.W - main_panel_width) // 2
                main_panel_y = 180
                
                pygame.draw.rect(self.screen, DARK_BEIGE, 
                                (main_panel_x + 10, main_panel_y + 10, 
                                main_panel_width, main_panel_height), 
                                border_radius=30)
                
                pygame.draw.rect(self.screen, BEIGE, 
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
                    pygame.draw.rect(self.screen, color, 
                                    (main_panel_x + 50, achievement_y, 
                                    main_panel_width - 100, achievement_height), 
                                    border_radius=15)
                    
                    # Texte
                    draw_text(achievement["name"], SMALL_FONT, BLACK, self.screen, 
                            main_panel_x + 400, achievement_y + 20)
                    
                    description_font = pygame.font.SysFont(None, 30)
                    draw_text(achievement["description"], description_font, GRAY, self.screen, 
                            main_panel_x + 400, achievement_y + 50)
                    
                    # Icône
                    if achievement["completed"]:
                        pygame.draw.circle(self.screen, DARK_BLUE, 
                                        (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                        20)
                        pygame.draw.line(self.screen, WHITE, 
                                        (main_panel_x + 90, achievement_y + achievement_height // 2), 
                                        (main_panel_x + 100, achievement_y + achievement_height // 2 + 10), 
                                        4)
                        pygame.draw.line(self.screen, WHITE, 
                                        (main_panel_x + 100, achievement_y + achievement_height // 2 + 10), 
                                        (main_panel_x + 115, achievement_y + achievement_height // 2 - 10), 
                                        4)
                    else:
                        pygame.draw.circle(self.screen, GRAY, 
                                        (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                        20)
                        pygame.draw.circle(self.screen, color, 
                                        (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                        16)
                    
                    achievement_y += achievement_height + 10
                
                # Bouton de retour
                back_button_rect = draw_textbox("RETOUR", self.W // 2 - 100, self.H - 100, 
                                            200, 50, SMALL_FONT, BLACK, ORANGE, self.screen, 25)
                
                if mouse_clicked and back_button_rect.collidepoint(mouse_pos):
                    if has_sound:
                        button_sound.play()
                    current_screen = "menu"
                
            
            # Afficher la version
            version_text = "DRAWWY v1.0"
            version_font = pygame.font.SysFont(None, 24)
            text_surface = version_font.render(version_text, True, BLACK)
            self.screen.blit(text_surface, (20, self.H - 30))
            
            pygame.display.flip()
            clock.tick(60)  # Limiter à 60 FPS

        pygame.quit()
        sys.exit()