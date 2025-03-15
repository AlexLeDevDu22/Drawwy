import pygame
import sys
import math
import random
from pygame import gfxdraw
import time
import yaml
import os

from shared.ui.common_ui import *

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

W,H = pygame.display.Info().current_w, pygame.display.Info().current_h

# Définition des thèmes et des données d'exemple d'images
themes = [
    {"name": "Paysage", "color": GREEN, "icon": "🏞️"},
    {"name": "Nourriture", "color": YELLOW, "icon": "🍔"},
    {"name": "Animaux", "color": BLUE, "icon": "🦁"},
    {"name": "Mode", "color": PINK, "icon": "👗"},
]

# Images fictives pour chaque thème (normalement chargées depuis Internet)
def generate_placeholder_images(theme, theme_index, count=10):
    # theme_color = themes[theme_index]["color"]
    # images = []
    
    # for i in range(count):
    #     # Créer une surface pour représenter une image
    #     img_surface = pygame.Surface((300, 300))
        
    #     # Remplir avec la color du thème
    #     img_surface.fill(theme_color)
        
    #     # Ajouter des formes aléatoires pour différencier chaque image
    #     for _ in range(10):
    #         shape_color = (
    #             random.randint(max(0, theme_color[0]-50), min(255, theme_color[0]+50)),
    #             random.randint(max(0, theme_color[1]-50), min(255, theme_color[1]+50)),
    #             random.randint(max(0, theme_color[2]-50), min(255, theme_color[2]+50))
    #         )
            
    #         shape_type = random.choice(["rect", "circle", "line"])
            
    #         if shape_type == "rect":
    #             x = random.randint(0, 250)
    #             y = random.randint(0, 250)
    #             w = random.randint(20, 100)
    #             h = random.randint(20, 100)
    #             pygame.draw.rect(img_surface, shape_color, (x, y, w, h))
            
    #         elif shape_type == "circle":
    #             x = random.randint(20, 280)
    #             y = random.randint(20, 280)
    #             r = random.randint(10, 50)
    #             pygame.draw.circle(img_surface, shape_color, (x, y), r)
            
    #         else:  # line
    #             x1 = random.randint(0, 300)
    #             y1 = random.randint(0, 300)
    #             x2 = random.randint(0, 300)
    #             y2 = random.randint(0, 300)
    #             pygame.draw.line(img_surface, shape_color, (x1, y1), (x2, y2), random.randint(2, 8))
        
    #     # Ajouter du texte pour identifier l'image
    #     text = info_font.render(f"Image {i+1}", True, WHITE)
    #     text_rect = text.get_rect(center=(150, 150))
    #     img_surface.blit(text, text_rect)
        
    #     images.append(img_surface)

    images=[]
    for i in range(len(os.listdir(f"assets/soloImages/{themes[theme]['name']}"))):
        image=pygame.image.load(f"assets/soloImages/{themes[theme]["name"]}/{i}.jpeg")
        images.append(image)
    
    return images


class ImageCarousel:
    def __init__(self, X, Y, images):
        self.W = W
        self.H = H
        self.carousel_height=200
        self.size = 0.6 * H
        self.rect = pygame.Rect((X - self.size) // 2, (Y - self.size) // 2, self.size, self.size)
        self.images = images
        self.current_offset = 0  # Position actuelle des images
        self.deceleration = 0.2  # Décélération progressive
        self.is_spinning = False
        self.selection_time = 0
        self.selection_delay = 3  # Temps avant l'arrêt
        self.shake_intensity = 0
        self.selected_image = None
        self.spin_speed=0
        self.max_spin_speed = 40
        self.particles=[]
        self.images_opacity=0
        
    def start_spin(self):
        self.is_spinning = True
        self.spin_speed = random.randint(self.max_spin_speed-20, self.max_spin_speed)  # Relancer avec la vitesse max
        self.selection_time = time.time() + self.selection_delay
    
    def update(self):
        if self.is_spinning:
            self.current_offset += self.spin_speed
            self.current_offset %= len(self.images) * self.carousel_height  # Boucle continue
            current_time = time.time()
            self.images_opacity = min(1, self.images_opacity + 0.01)

            if current_time >= self.selection_time:
                distance_to_target = (self.carousel_height//2-self.current_offset%self.carousel_height)%self.carousel_height
                if self.spin_speed > 0:
                    self.spin_speed = max(0, self.spin_speed - self.deceleration)
                    if distance_to_target < 10 and self.spin_speed < 5:
                        self.spin_speed = max(0.5, self.spin_speed - random.randint(0.1,0.5))
                else:
                    if distance_to_target>1:
                        if distance_to_target<=self.carousel_height//2:
                            self.current_offset+=math.sqrt(distance_to_target)
                        else:
                            self.current_offset-=math.sqrt(distance_to_target)
                    else:
                        self.is_spinning = False
                        self.selected_image = (round(self.current_offset / self.carousel_height)+1) % len(self.images)

                        self.shake_intensity = 0

                        # Ajouter des particules pour célébrer la sélection
                        for _ in range(50):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(2, 6)
                            size = random.uniform(3, 8)
                            life = random.uniform(70, 100)
                            color = random.choice([YELLOW, PINK, GREEN, BLUE])
                            self.particles.append({
                                'x': self.rect.centerx,
                                'y': self.rect.centery,
                                'vx': math.cos(angle) * speed,
                                'vy': math.sin(angle) * speed,
                                'size': size,
                                'life': life,
                                'color': color
                            })

            self.shake_intensity = max(0, self.shake_intensity - 0.1) if not self.is_spinning else min(10, self.shake_intensity + 0.2)

        # Mettre à jour les particules
        for i, particle in enumerate(self.particles):
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravité
            particle['life'] -= 1
        
        # Supprimer les particules expirées
        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self, surface):
        center_x = self.rect.centerx
        for i, img in enumerate(self.images):
            shake_x = random.uniform(-self.shake_intensity*(self.spin_speed/self.max_spin_speed), self.shake_intensity*(self.spin_speed/self.max_spin_speed))
            shake_y = random.uniform(-self.shake_intensity*(self.spin_speed/self.max_spin_speed), self.shake_intensity*(self.spin_speed/self.max_spin_speed))

            pos_x = (i * self.carousel_height - self.current_offset + center_x) % (len(self.images) * self.carousel_height) - self.carousel_height//2
            scale_factor = max(0.2, 1 - abs(center_x - pos_x) / (self.W // 2))
            alpha = max(0, 255 * scale_factor* self.images_opacity)

            scaled_img = pygame.transform.scale(img, (int(self.carousel_height * scale_factor), int(self.carousel_height * scale_factor)))
            img_surface = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)

            # Créer un rectangle avec des coins arrondis pour le masque
            mask = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), mask.get_rect(), border_radius=20)

            # Appliquer le masque arrondi à l'image
            img_surface.fill((255, 255, 255, int(alpha)))
            img_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            img_surface.blit(scaled_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # Blitter l'image arrondie sur la surface principale
            surface.blit(img_surface, (pos_x - scaled_img.get_width() // 2, self.rect.centery - scaled_img.get_height() // 2))

        transparent_surface = pygame.Surface((self.carousel_height, self.carousel_height), pygame.SRCALPHA)  # Taille du rectangle
        transparent_surface.fill((0, 0, 0, 0))  # Totalement transparent

        main_frame_rect = pygame.Rect(
            self.rect.centerx - self.carousel_height//2,
            self.rect.centery - self.carousel_height//2,
            self.carousel_height,
            self.carousel_height
        )
        # Appliquer les tremblements
        shake_x = random.uniform(-self.shake_intensity*(self.spin_speed/self.max_spin_speed), self.shake_intensity*(self.spin_speed/self.max_spin_speed))
        shake_y = random.uniform(-self.shake_intensity*(self.spin_speed/self.max_spin_speed), self.shake_intensity*(self.spin_speed/self.max_spin_speed))
        main_frame_rect.x += shake_x
        main_frame_rect.y += shake_y

        # Dessiner le rectangle avec des bordures uniquement (intérieur transparent)
        border_color = (255, 255, 255)  # Blanc
        border_radius = 20  # Coins arrondis
        border_width = 5  # Épaisseur des bordures

        pygame.draw.rect(surface, border_color, main_frame_rect, width=border_width, border_radius=border_radius)

        # Dessiner les particules
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 100))
            particle_color = (*particle['color'], alpha)
            gfxdraw.filled_circle(
                surface, 
                int(particle['x']), 
                int(particle['y']), 
                int(particle['size']), 
                particle_color
            )

class Button:
    def __init__(self, x, y, W, H, text, color, hover_color, text_color=WHITE, border_radius=15):
        self.rect = pygame.Rect(x, y, W, H)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.is_hovered = False
        self.animation_progress = 0
        self.scale = 1.0
        
    def draw(self, surface):
        # Animation de survol
        if self.is_hovered and self.animation_progress < 1:
            self.animation_progress += 0.1
        elif not self.is_hovered and self.animation_progress > 0:
            self.animation_progress -= 0.1
        
        self.animation_progress = max(0, min(1, self.animation_progress))
        
        # color interpolée
        color = [
            int(self.color[i] + (self.hover_color[i] - self.color[i]) * self.animation_progress)
            for i in range(3)
        ]
        
        # Échelle pour effet de survol
        self.scale = 1.0 + 0.05 * self.animation_progress
        scaled_W = int(self.rect.w * self.scale)
        scaled_H = int(self.rect.h * self.scale)
        
        # Position centrée pour l'animation
        scaled_x = self.rect.x + (self.rect.w - scaled_W) // 2
        scaled_y = self.rect.y + (self.rect.h - scaled_H) // 2
        
        # Dessiner le bouton arrondi
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_W, scaled_H)
        pygame.draw.rect(surface, color, scaled_rect, border_radius=self.border_radius)
        
        # Dessiner le texte
        text_surf = BUTTON_FONT.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        previous_hover = self.is_hovered
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered != previous_hover
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

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

def draw_background(surface):
    # Dégradé de fond bleu clair
    for y in range(H):
        # Interpolation entre deux colors pour créer un dégradé
        color = [
            int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / H))
            for i in range(3)
        ]
        pygame.draw.line(surface, color, (0, y), (W, y))

def image_selector(screen, theme_index):
    # Générer des images d'exemple pour le thème sélectionné
    images = generate_placeholder_images(theme_index, 15)
    
    # Créer la roulette d'images
    image_roulette = ImageCarousel(W,H, images)
    
    # Créer le bouton pour lancer la roulette
    spin_button = Button(W // 2 - 100, H*0.7, 200, 60, "Tourner", themes[theme_index]["color"], LIGHT_PURPLE)
    
    # Créer le bouton pour commencer à dessiner (initialement désactivé)
    start_drawing_button = Button(W // 2 - 100, H *0.7+80, 200, 60, "Dessiner", PURPLE, LIGHT_PURPLE)
    
    back_button = Button(W // 2 - 100, H *0.7+200, 200, 60, "Retour", PURPLE, LIGHT_PURPLE)
    
    # Créer des objets flottants pour l'arrière-plan
    floating_objects = []
    for _ in range(15):
        x = random.randint(-100, W+100)
        y = random.randint(0, H)
        size = random.randint(5, 15)
        color_choice = random.choice([PINK, YELLOW, BLUE, GREEN])
        speed = random.uniform(0.2, 0.8)
        floating_objects.append(FloatingObject(x, y, size, color_choice, speed))
    
    # Variables d'état
    running = True
    countdown_start_time = 0
    show_countdown = False

    clock=pygame.time.Clock()
    
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Vérifier le clic sur le bouton de rotation
                if spin_button.is_clicked(mouse_pos) and not image_roulette.is_spinning:
                    image_roulette.start_spin()
                
                # Vérifier le clic sur le bouton de dessin
                if start_drawing_button.is_clicked(mouse_pos) and image_roulette.selected_image:
                    # Lancer le compte à rebours
                    if not show_countdown:
                        show_countdown = True
                        countdown_start_time = time.time()
                    # Si on voulait passer à la page suivante, ce serait ici
                    print("Lancement de l'interface de dessin...")

                if back_button.is_clicked(mouse_pos):
                    return screen ,"theme"
        
        # Mettre à jour les survols
        spin_button.check_hover(mouse_pos)
        if image_roulette.selected_image:
            start_drawing_button.check_hover(mouse_pos)

        back_button.check_hover(mouse_pos)
        
        # Mettre à jour les objets flottants
        for obj in floating_objects:
            obj.update()
        
        # Mettre à jour la roulette d'images
        image_roulette.update()
        
        # Dessiner l'arrière-plan
        draw_background(screen)
        
        # Dessiner les objets flottants
        for obj in floating_objects:
            obj.draw(screen)
       
        
        # Dessiner le titre avec une ombre
        title_shadow = TITLE_FONT.render("DRAWWY", True, BLACK)
        title_shadow_rect = title_shadow.get_rect(center=(W//2+4, 104))
        screen.blit(title_shadow, title_shadow_rect)
        
        title = TITLE_FONT.render("DRAWWY", True, WHITE)
        title_rect = title.get_rect(center=(W//2, 100))
        screen.blit(title, title_rect)
        
        # Dessiner le sous-titre avec le thème sélectionné
        subtitle = BUTTON_FONT.render(f"Thème: {themes[theme_index]['name']}", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(W//2, 220))
        screen.blit(subtitle, subtitle_rect)
        
        # Dessiner la roulette d'images
        image_roulette.draw(screen)
        
        # Dessiner le bouton de rotation
        if not image_roulette.selected_image or not image_roulette.is_spinning:
            spin_button.draw(screen)
        
        # Dessiner le bouton de dessin si une image est sélectionnée
        if image_roulette.selected_image:
            start_drawing_button.draw(screen)
        
        # Afficher le compte à rebours si actif
        if show_countdown:
            elapsed = time.time() - countdown_start_time
            if elapsed < 3:
                countdown_value = 3 - int(elapsed)
                countdown_text = BUTTON_FONT.render(str(countdown_value), True, WHITE)
                countdown_rect = countdown_text.get_rect(center=(W//2, H//2))
                
                # Ajouter un effet de pulsation
                scale = 1.0 + 0.2 * math.sin(elapsed * 10)
                countdown_text = pygame.transform.scale(
                    countdown_text, 
                    (int(countdown_rect.w * scale), int(countdown_rect.h * scale))
                )
                countdown_rect = countdown_text.get_rect(center=(W//2, H//2))
                
                # Dessiner un cercle d'arrière-plan
                pygame.draw.circle(screen, PURPLE, (W//2, H//2), 80 * scale, 0)
                screen.blit(countdown_text, countdown_rect)
            else:
                # Le compte à rebours est terminé, on lancerait normalement la prochaine page
                show_countdown = False
                
                return screen, "play", image_roulette.selected_image
        
        # Mettre à jour l'affichage
        pygame.display.flip()
        clock.tick(config["fps"])
    
    return None  # À remplacer par un retour vers la page suivante
