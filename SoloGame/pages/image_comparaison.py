from shared.ui.common_ui import *
from shared.ui.elements import Button
from shared.utils.data_manager import *

import pygame
import sys
import math
import random
from pygame import gfxdraw
import time
import os

W, H = pygame.display.Info().current_w, pygame.display.Info().current_h

# Définition des thèmes et des données d'exemple d'images
themes = [
    {"name": "Paysage", "color": GREEN, "icon": "🏞️"},
    {"name": "Nourriture", "color": YELLOW, "icon": "🍔"},
    {"name": "Animaux", "color": BLUE, "icon": "🦁"},
    {"name": "Mode", "color": PINK, "icon": "👗"},
]

class ImageComparison:
    def __init__(self, original_img, redrawn_img):
        self.W = W
        self.H = H
        self.original_img = original_img
        self.redrawn_img = redrawn_img
        self.image_size = min(W * 0.4, H * 0.6)  # Taille adaptative pour l'affichage
        self.original_rect = pygame.Rect(W * 0.25 - self.image_size / 2, H * 0.45 - self.image_size / 2, 
                                         self.image_size, self.image_size)
        self.redrawn_rect = pygame.Rect(W * 0.75 - self.image_size / 2, H * 0.45 - self.image_size / 2, 
                                        self.image_size, self.image_size)
        self.particles = []
        self.fade_in = 0  # Pour l'animation de fondu
        self.show_comparison = False
        self.comparison_start_time = 0
        
    def start_comparison(self):
        self.show_comparison = True
        self.comparison_start_time = time.time()
        
        # Ajouter des particules pour l'effet de transition
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            size = random.uniform(3, 8)
            life = random.uniform(70, 100)
            color = random.choice([YELLOW, PINK, GREEN, BLUE])
            self.particles.append({
                'x': self.W // 2,
                'y': self.H // 2,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'life': life,
                'color': color
            })
    
    def update(self):
        # Animation de fondu en entrée
        if self.fade_in < 1:
            self.fade_in += 0.02
        
        # Mettre à jour les particules
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # Gravité
            particle['life'] -= 1
        
        # Supprimer les particules expirées
        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self, surface):
        # Préparer les images avec des coins arrondis et le fondu
        for idx, (img, rect) in enumerate([(self.original_img, self.original_rect), 
                                          (self.redrawn_img, self.redrawn_rect)]):
            
            # Redimensionner l'image
            scaled_img = pygame.transform.scale(img, (int(self.image_size), int(self.image_size)))
            
            # Créer une surface avec canal alpha
            img_surface = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
            
            # Créer un masque avec des coins arrondis
            mask = pygame.Surface(scaled_img.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255), mask.get_rect(), border_radius=20)
            
            # Appliquer le fondu et le masque
            alpha = int(255 * self.fade_in)
            img_surface.fill((255, 255, 255, alpha))
            img_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            img_surface.blit(scaled_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Dessiner l'image sur la surface principale
            surface.blit(img_surface, rect)
            
            # Dessiner une bordure autour de l'image
            border_color = WHITE
            border_width = 3
            pygame.draw.rect(surface, border_color, rect, 
                             width=border_width, border_radius=20)
            
            # Ajouter des étiquettes sous les images
            label_text = "Image Originale" if idx == 0 else "Image Redessinée"
            label = BUTTON_FONT.render(label_text, True, WHITE)
            label_rect = label.get_rect(center=(rect.centerx, rect.bottom + 40))
            surface.blit(label, label_rect)
        
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
            
        # Animation de comparaison si active
        if self.show_comparison:
            elapsed = time.time() - self.comparison_start_time
            if elapsed < 2:
                # Effet de flash ou d'animation entre les deux images
                flash_intensity = math.sin(elapsed * 10) * 0.5 + 0.5
                flash_surface = pygame.Surface((W, H), pygame.SRCALPHA)
                flash_surface.fill((255, 255, 255, int(flash_intensity * 50)))
                surface.blit(flash_surface, (0, 0))
                
                # Texte de comparaison
                compare_text = TITLE_FONT.render("COMPARAISON", True, WHITE)
                compare_rect = compare_text.get_rect(center=(W//2, H//2))
                
                # Effet de pulsation
                scale = 1.0 + 0.1 * math.sin(elapsed * 15)
                compare_text = pygame.transform.scale(
                    compare_text, 
                    (int(compare_rect.w * scale), int(compare_rect.h * scale))
                )
                compare_rect = compare_text.get_rect(center=(W//2, H//2))
                surface.blit(compare_text, compare_rect)
            else:
                self.show_comparison = False


class FloatingObject:
    def __init__(self, x, y, size, color, speed):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed
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


def image_comparison_screen(screen, original_img_id, redrawn_img_path=None):
    # Charger l'image originale
    theme_folders = [theme["name"] for theme in themes]
    theme_index = 0  # Valeur par défaut
    
    for theme_idx, theme_name in enumerate(theme_folders):
        if os.path.exists(f"assets/soloImages/{theme_name}/{original_img_id}.jpeg"):
            original_img = pygame.image.load(f"assets/soloImages/{theme_name}/{original_img_id}.jpeg")
            theme_index = theme_idx
            break
    else:
        # Si aucune image n'est trouvée, créer une image factice
        original_img = pygame.Surface((300, 300))
        original_img.fill(themes[0]["color"])  # Utiliser la couleur du premier thème
    
    # Charger l'image redessinée (ou utiliser une image fictive pour la démonstration)
    if redrawn_img_path and os.path.exists(redrawn_img_path):
        redrawn_img = pygame.image.load(redrawn_img_path)
    else:
        # Créer une image fictive modifiée pour la démonstration
        redrawn_img = original_img.copy()
        # Ajouter un effet pour simuler une version redessinée
        for _ in range(5000):
            x = random.randint(0, redrawn_img.get_width()-1)
            y = random.randint(0, redrawn_img.get_height()-1)
            color = redrawn_img.get_at((x, y))
            # Modifier légèrement la couleur
            new_color = (
                min(255, max(0, color[0] + random.randint(-30, 30))),
                min(255, max(0, color[1] + random.randint(-30, 30))),
                min(255, max(0, color[2] + random.randint(-30, 30))),
                color[3] if len(color) > 3 else 255
            )
            redrawn_img.set_at((x, y), new_color)
    
    # Créer l'objet de comparaison d'images
    comparison = ImageComparison(original_img, redrawn_img)
    
    # Créer des boutons
    compare_button = Button(W//2 - 150, H * 0.75, w=120, text="Comparer")
    back_button = Button(W//2 + 30, H * 0.75, w=120, text="Retour")
    save_button = Button(W//2 - 60, H * 0.85, w=120, text="Sauvegarder")
    
    # Créer des objets flottants pour l'arrière-plan
    floating_objects = []
    for _ in range(15):
        x = random.randint(-100, W+100)
        y = random.randint(0, H)
        size = random.randint(5, 15)
        color_choice = random.choice([PINK, YELLOW, BLUE, GREEN])
        speed = random.uniform(0.2, 0.8)
        floating_objects.append(FloatingObject(x, y, size, color_choice, speed))
    
    clock = pygame.time.Clock()
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if compare_button.check_hover(mouse_pos):
                    comparison.start_comparison()
                
                if back_button.check_hover(mouse_pos):
                    return screen, "themes", None
                
                if save_button.check_hover(mouse_pos):
                    # Logique pour sauvegarder l'image
                    print("Sauvegarde de l'image...")
                    # Vous pourriez implémenter ici un dialogue de sauvegarde
                    # ou enregistrer directement dans un dossier prédéfini
        
        # Mettre à jour les survols des boutons
        compare_button.check_hover(mouse_pos)
        back_button.check_hover(mouse_pos)
        save_button.check_hover(mouse_pos)
        
        # Mettre à jour les objets flottants
        for obj in floating_objects:
            obj.update()
        
        # Mettre à jour la comparaison d'images
        comparison.update()
        
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
        
        # Dessiner le sous-titre
        subtitle = BUTTON_FONT.render("Comparer les Images", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(W//2, 160))
        screen.blit(subtitle, subtitle_rect)
        
        # Dessiner les images comparées
        comparison.draw(screen)
        
        # Dessiner les boutons
        compare_button.draw(screen)
        back_button.draw(screen)
        save_button.draw(screen)
        
        # Mettre à jour l'affichage
        pygame.display.flip()
        clock.tick(CONFIG["fps"])


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("DRAWWY - Comparaison d'Images")
    
    # Si vous avez un ID d'image spécifique à charger, vous pouvez le spécifier ici
    # Sinon, vous pourriez choisir une image aléatoire ou afficher une interface de sélection
    original_img_id = 0  # Par exemple, chargez l'image 0
    
    # Si vous avez une image redessinée à charger, vous pouvez spécifier son chemin
    redrawn_img_path = None  # Par exemple, "assets/redrawn/my_drawing.png"
    
    # Lancer l'écran de comparaison d'images
    image_comparison_screen(screen, original_img_id, redrawn_img_path)

