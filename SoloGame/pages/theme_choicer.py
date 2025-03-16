from shared.ui.common_ui import *
from shared.ui.elements import *

import pygame
import sys
import math
import random
from pygame import gfxdraw
try:from pygame_emojis import load_emoji
except:import pygame.freetype 
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Définition des thèmes
themes = [
    {"nom": "Paysage", "couleur": GREEN, "icone": "🏞️"},
    {"nom": "Nourriture", "couleur": YELLOW, "icone": "🍔"},
    {"nom": "Animaux", "couleur": BLUE, "icone": "🦁"},
    {"nom": "Mode", "couleur": PINK, "icone": "👗"},
]
W,H = pygame.display.Info().current_w, pygame.display.Info().current_h

class ThemeCard:
    def __init__(self, x, y, width, height, theme_info):
        self.rect = pygame.Rect(x, y, width, height)
        self.y = y
        self.theme_info = theme_info
        self.color = theme_info["couleur"]
        self.light_color = self.lighten_color(self.color, 30)
        self.is_hovered = False
        self.is_selected = False
        self.animation_progress = 0
        self.hover_scale = 1.0
        self.rotation = 0
        self.particles = []
        
    def lighten_color(self, color, amount):
        return tuple(min(255, c + amount) for c in color)
    
    def draw(self, screen):
        # Animation de survol
        if (self.is_hovered or self.is_selected) and self.animation_progress < 1:
            self.animation_progress += 0.1
        elif not self.is_hovered and not self.is_selected and self.animation_progress > 0:
            self.animation_progress -= 0.1
        
        self.animation_progress = max(0, min(1, self.animation_progress))
        
        # Animation de sélection
        if self.is_selected:
            self.rotation = (self.rotation + 1) % 360
            
            # Ajouter des particules quand sélectionné
            if random.random() < 0.2:
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1, 3)
                size = random.uniform(3, 6)
                life = random.uniform(20, 40)
                px = self.rect.centerx + random.uniform(-self.rect.width/2, self.rect.width/2)
                py = self.rect.centery + random.uniform(-self.rect.height/2, self.rect.height/2)
                self.particles.append({
                    'x': px, 'y': py,
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed,
                    'size': size, 'life': life,
                    'color': self.light_color
                })
        
        # Mettre à jour et dessiner les particules
        for i, particle in enumerate(self.particles):
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            alpha = int(255 * (abs(particle['life']) / 40))
            particle_color = (*particle['color'], alpha)
            
            gfxdraw.filled_circle(screen, 
                                 int(particle['x']), 
                                 int(particle['y']), 
                                 int(particle['size']), 
                                 particle_color)
        
        # Supprimer les particules expirées
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # Échelle pour effet de survol
        self.hover_scale = 1.0 + 0.08 * self.animation_progress
        scaled_width = int(self.rect.width * self.hover_scale)
        scaled_height = int(self.rect.height * self.hover_scale)
        
        # Position centrée pour l'animation
        scaled_x = self.rect.x + (self.rect.width - scaled_width) // 2
        scaled_y = self.rect.y + (self.rect.height - scaled_height) // 2
        
        # Couleur interpolée
        color = [
            int(self.color[i] + (self.light_color[i] - self.color[i]) * self.animation_progress)
            for i in range(3)
        ]
        
        # Dessiner la bordure si sélectionnée
        if self.is_selected:
            border_rect = pygame.Rect(scaled_x-10, scaled_y-10, scaled_width+20, scaled_height+20)
            pygame.draw.rect(screen, WHITE, border_rect, border_radius=20)
            
            # Effet de brillance autour de la carte
            for i in range(5):
                glow_size = 5 - i
                glow_rect = pygame.Rect(
                    border_rect.x - glow_size,
                    border_rect.y - glow_size,
                    border_rect.width + glow_size * 2,
                    border_rect.height + glow_size * 2
                )
                glow_color = (*self.light_color, 50 - i*10)
                pygame.draw.rect(screen, glow_color, glow_rect, border_radius=25, width=2)
        
        # Dessiner la carte
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        pygame.draw.rect(screen, color, scaled_rect, border_radius=15)
        
        # Dessiner l'icône
        icone_texte = MEDIUM_FONT.render(self.theme_info["icone"], True, WHITE)
        icone_rect = icone_texte.get_rect(center=(scaled_rect.centerx, scaled_rect.centery - 30))
        screen.blit(icone_texte, icone_rect)

        try: # pygame emojis
            screen.blit(load_emoji(self.theme_info["icone"], (16/100*H, 16/100*H)), (scaled_rect.centerx-85, scaled_rect.centery - 108))
        except: # pygame freetype
            seguisy80 = pygame.freetype.SysFont("segoeuisymbol", 135)
            emoji, rect = seguisy80.render(self.theme_info["icone"], "black")
            rect.center = (scaled_rect.centerx, scaled_rect.centery)
            screen.blit(emoji, rect)
        
        # Dessiner le nom du thème
        nom_texte = MEDIUM_FONT.render(self.theme_info["nom"], True, SOFT_ORANGE)
        nom_rect = nom_texte.get_rect(center=(scaled_rect.centerx+2, scaled_rect.centery + 62))
        screen.blit(nom_texte, nom_rect)

        nom_texte = MEDIUM_FONT.render(self.theme_info["nom"], True, WHITE)
        nom_rect = nom_texte.get_rect(center=(scaled_rect.centerx, scaled_rect.centery + 60))
        screen.blit(nom_texte, nom_rect)
    
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
    
    def draw(self, screen):
        # Dessiner un cercle flou
        for i in range(5):
            radius = self.size - i
            alpha = 100 - i * 20
            gfxdraw.filled_circle(screen, int(self.x), int(self.y), radius, (*self.color, alpha))

def draw_background(screen):
    # Dégradé de fond
    for y in range(H):
        # Interpolation entre deux couleurs pour créer un dégradé
        color = [
            int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / H))
            for i in range(3)
        ]
        pygame.draw.line(screen, color, (0, y), (W, y))

def theme_choicer(screen):
    # Créer les cartes de thèmes
    theme_width, theme_height = 200, 200
    theme_cards = []
    
    for i, theme in enumerate(themes):
        x = W // 2 - (len(themes) * (theme_width + 30)) // 2 + i * (theme_width + 30)
        y = H // 3
        theme_cards.append(ThemeCard(x, y, theme_width, theme_height, theme))
    # Créer le bouton de démarrage
    start_button = Button("center", H // 3*2-20, text="Commencer", active=False)
    quit_button = Button("center", H // 3*2+110, text="Quitter")
    
    # Créer des objets flottants pour l'arrière-plan
    floating_objects = []
    for _ in range(30):
        x = random.randint(-100, W+100)
        y = random.randint(0, H)
        size = random.randint(5, 15)
        color_choice = random.choice([PINK, YELLOW, BLUE, GREEN])
        speed = random.uniform(0.2, 0.8)
        floating_objects.append(FloatingObject(x, y, size, color_choice, speed))
    
    # Variables de jeu
    selected_theme = None
    running = True

    clock = pygame.time.Clock()
    
    # Animation d'introduction
    intro_alpha = 255
    intro_stage = 0
    intro_timer = 0
    
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for i, card in enumerate(theme_cards):
            if card.rect.collidepoint(mouse_pos):
                card.is_hovered = True
            else:
                card.is_hovered = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and intro_stage >= 2:
                # Vérifier les clics sur les cartes de thèmes
                for i, card in enumerate(theme_cards):
                    if card.is_hovered:
                        # Désélectionner toutes les cartes
                        for c in theme_cards:
                            c.is_selected = False
                        # Sélectionner la carte cliquée
                        card.is_selected = True
                        selected_theme = i

                        start_button.active=True
                
                
                # Vérifier le clic sur le bouton de démarrage
                if start_button.rect.collidepoint(mouse_pos) and selected_theme is not None:
                    print(f"Thème sélectionné: {themes[selected_theme]['nom']}")
                    return screen, "images", selected_theme
                if quit_button.rect.collidepoint(mouse_pos):
                    return screen, "exit", selected_theme
        
        # Mettre à jour les survols
        if intro_stage >= 2:
            for card in theme_cards:
                card.rect.collidepoint(mouse_pos)
            
            start_button.check_hover(mouse_pos)
            quit_button.check_hover(mouse_pos)
        
        # Mettre à jour les objets flottants
        for obj in floating_objects:
            obj.update()
        
        # Dessiner l'arrière-plan
        draw_background(screen)
        
        # Dessiner les objets flottants
        for obj in floating_objects:
            obj.draw(screen)
        
        # Animation d'introduction
        if intro_stage == 0:
            # Fondu d'entrée
            intro_alpha -= 3
            if intro_alpha <= 0:
                intro_alpha = 0
                intro_stage = 1
                intro_timer = 60  # Attendre 1 seconde
            
            # Dessiner un rectangle noir qui disparaît
            intro_surf = pygame.Surface((W, H))
            intro_surf.fill(BLACK)
            intro_surf.set_alpha(intro_alpha)
            screen.blit(intro_surf, (0, 0))
        
        elif intro_stage == 1:
            # Attendre un moment
            intro_timer -= 1
            if intro_timer <= 0:
                intro_stage = 2
        
        else:
            # Animation terminée, afficher l'interface
            
            # Dessiner le titre avec une ombre
            title_shadow = TITLE_FONT.render("DRAWWY", True, BLACK)
            title_shadow_rect = title_shadow.get_rect(center=(W//2+4, 104))
            screen.blit(title_shadow, title_shadow_rect)
            
            title = TITLE_FONT.render("DRAWWY", True, WHITE)
            title_rect = title.get_rect(center=(W//2, 100))
            screen.blit(title, title_rect)
            
            # Dessiner le sous-titre
            subtitle = BUTTON_FONT.render("Sélectionne un thème", True, WHITE)
            subtitle_rect = subtitle.get_rect(center=(W//2, 200))
            screen.blit(subtitle, subtitle_rect)

            
            # Dessiner les cartes de thèmes
            for i, card in enumerate(theme_cards):
                card.rect.y = card.y+math.sin((pygame.time.get_ticks()+16000/len(theme_cards)*i) / 1000) * 16
                card.draw(screen)
            
            # Dessiner le bouton de démarrage
            start_button.draw(screen)
            quit_button.draw(screen)
        
        # Mettre à jour l'affichage
        pygame.display.flip()
        clock.tick(config["fps"])