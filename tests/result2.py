import pygame
import math
import sys
import random
from pygame.locals import *
from pygame import gfxdraw
from shared.ui.common_ui import *
# Initialisation
pygame.init()
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animation de Score")


# Police
font_large = pygame.font.SysFont('Arial', 36, bold=True)
font_medium = pygame.font.SysFont('Arial', 24)

def draw_background(surface):
    # Dégradé de fond bleu clair
    for y in range(HEIGHT):
        # Interpolation entre deux couleurs pour créer un dégradé
        color = [
            int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / HEIGHT))
            for i in range(3)
        ]
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particles(self, x, y, color, count=20, speed_range=(1, 3), size_range=(2, 5), life_range=(30, 60)):
        """Ajoute plusieurs particules à partir d'une position donnée"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            size = random.uniform(*size_range)
            life = random.uniform(*life_range)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'life': life,
                'max_life': life,
                'color': color,
                'gravity': random.uniform(0.02, 0.08)
            })
    
    def add_confetti(self, x, y, count=1):
        """Ajoute des confettis colorés"""
        colors = [GOLD, BLUE, PINK, GREEN, YELLOW]
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            size = random.uniform(3, 8)
            life = random.uniform(60, 120)
            rotation_speed = random.uniform(-5, 5)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'life': life,
                'max_life': life,
                'color': random.choice(colors),
                'gravity': random.uniform(0.02, 0.08),
                'type': 'confetti',
                'rotation': random.uniform(0, 360),
                'rotation_speed': rotation_speed
            })
    
    def update(self):
        """Met à jour toutes les particules"""
        for particle in self.particles:
            # Mise à jour de la position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Appliquer la gravité
            particle['vy'] += particle['gravity']
            
            # Réduire la durée de vie
            particle['life'] -= 1
            
            # Mettre à jour la rotation pour les confettis
            if 'type' in particle and particle['type'] == 'confetti':
                particle['rotation'] += particle['rotation_speed']
        
        # Supprimer les particules expirées
        self.particles = [p for p in self.particles if p['life'] > 0]
    
    def draw(self, surface):
        """Dessine toutes les particules actives"""
        for particle in self.particles:
            # Calculer l'opacité basée sur la durée de vie restante
            alpha = int(255 * (particle['life'] / particle['max_life']))
            
            if 'type' in particle and particle['type'] == 'confetti':
                # Dessiner un confetti (rectangle avec rotation)
                rect_surface = pygame.Surface((particle['size'] * 2, particle['size']), pygame.SRCALPHA)
                pygame.draw.rect(rect_surface, (*particle['color'], alpha), 
                                (0, 0, particle['size'] * 2, particle['size']))
                
                # Rotation du confetti
                rotated_surface = pygame.transform.rotate(rect_surface, particle['rotation'])
                rotated_rect = rotated_surface.get_rect(center=(particle['x'], particle['y']))
                surface.blit(rotated_surface, rotated_rect)
            else:
                # Dessiner une particule circulaire standard avec gfxdraw pour le support de l'alpha
                gfxdraw.filled_circle(
                    surface, 
                    int(particle['x']), 
                    int(particle['y']), 
                    int(particle['size']), 
                    (*particle['color'], alpha)
                )

class PopupAnimation:
    def __init__(self, score, images=None):
        self.score = score
        self.popup_width, self.popup_height = 600, 400
        self.popup_x = (WIDTH - self.popup_width) // 2
        self.popup_y = -self.popup_height  # Commencer hors écran
        self.target_y = (HEIGHT - self.popup_height) // 2
        
        # Animation de transition
        self.animation_speed = 5
        self.animation_done = False
        self.animation_progress = 0
        
        # Images (à remplacer par vos images)
        self.images = images or [pygame.Surface((250, 150)), pygame.Surface((250, 150))]
        self.images[0].fill(WHITE)
        self.images[1].fill(WHITE)
        
        # Animation des étoiles
        self.stars_fill = [0, 0, 0]  # Pourcentage de remplissage de chaque étoile
        self.star_animation_speed = 2
        self.stars_filled = False
        self.star_jump = [0, 0, 0]
        self.star_rotation = [0, 0, 0]
        
        # Détermine combien d'étoiles sont remplies
        self.filled_stars = 0
        if score >= 70:
            self.filled_stars = 3
        elif score >= 50:
            self.filled_stars = 2
        elif score >= 30:
            self.filled_stars = 1
        
        # Système de particules
        self.particles = ParticleSystem()
        self.particle_timer = 0
        self.shine_angle = 0
        
        # Flags pour les événements d'animation
        self.entry_particles_created = False
        self.star_particles_created = [False, False, False]
    
    def update(self):
        # Animation d'entrée de la popup
        if self.popup_y < self.target_y:
            self.popup_y += self.animation_speed
            
            # Créer des particules pour l'entrée
            if not self.entry_particles_created and self.popup_y > 0:
                for _ in range(30):
                    self.particles.add_confetti(
                        random.randint(self.popup_x, self.popup_x + self.popup_width),
                        self.popup_y + self.popup_height,
                        count=1
                    )
                self.entry_particles_created = True
            
            if self.popup_y >= self.target_y:
                self.popup_y = self.target_y
                self.animation_done = True
                
                # Plus de particules quand l'animation est terminée
                for _ in range(40):
                    self.particles.add_confetti(
                        random.randint(self.popup_x, self.popup_x + self.popup_width),
                        self.popup_y,
                        count=1
                    )
        
        # Animation de remplissage des étoiles
        if self.animation_done and not self.stars_filled:
            all_filled = True
            for i in range(3):
                if i < self.filled_stars:
                    prev_fill = self.stars_fill[i]
                    self.stars_fill[i] += self.star_animation_speed
                    
                    # Créer des particules quand une étoile est remplie à 100%
                    if prev_fill < 100 and self.stars_fill[i] >= 100:
                        self.stars_fill[i] = 100
                        
                        # Position de l'étoile
                        star_size = 40
                        star_spacing = 120
                        start_x = self.popup_x + (self.popup_width - star_spacing * 2) // 2 - 20
                        star_y = self.popup_y + 180
                        star_x = start_x + i * star_spacing + star_size//2
                        
                        # Ajouter des particules d'étoile
                        self.particles.add_particles(
                            star_x, star_y + star_size//2, 
                            GOLD, count=50, 
                            speed_range=(1, 4), 
                            size_range=(2, 6)
                        )
                    
                    if self.stars_fill[i] < 100:
                        all_filled = False
            
            if all_filled:
                self.stars_filled = True
        
        # Animation de saut et rotation des étoiles
        if self.stars_filled:
            for i in range(self.filled_stars):
                # Fonction sinusoïdale pour le saut
                self.star_jump[i] = -10 * abs(math.sin(pygame.time.get_ticks() * 0.005 + i * 1.0))
                # Rotation lente
                self.star_rotation[i] = 5 * math.sin(pygame.time.get_ticks() * 0.003 + i * 0.7)
        
        # Particules en continu
        self.particle_timer += 1
        if self.stars_filled and self.particle_timer % 15 == 0:  # Toutes les 15 frames
            # Ajouter des particules autour du titre
            title_x = self.popup_x + self.popup_width // 2
            title_y = self.popup_y + 30
            self.particles.add_particles(
                title_x + random.randint(-100, 100),
                title_y + random.randint(-10, 20),
                random.choice([GOLD, BLUE, PINK]), 
                count=5
            )
        
        # Angle de brillance pour les effets
        self.shine_angle = (self.shine_angle + 2) % 360
        
        # Mettre à jour toutes les particules
        self.particles.update()
    
    def draw_star(self, x, y, size, fill_percent, jump_offset=0, rotation=0):
        # Créer une surface transparente
        star_surface = pygame.Surface((size * 2, size * 2+20), pygame.SRCALPHA)
        
        points = []
        for i in range(5):
            # Calcul des points extérieurs de l'étoile
            outer_x = x + size * math.cos(math.radians(rotation + i * 72 - 18))
            outer_y = y + jump_offset + size * math.sin(math.radians(rotation + i * 72 - 18))+20
            points.append((outer_x - x + size, outer_y - y + size))
            
            # Calcul des points intérieurs de l'étoile
            inner_x = x + size * 0.4 * math.cos(math.radians(rotation + i * 72 + 18))
            inner_y = y + jump_offset + size * 0.4 * math.sin(math.radians(rotation + i * 72 + 18))+20
            points.append((inner_x - x + size, inner_y - y + size))
        
        # Dessiner le contour de l'étoile
        pygame.draw.polygon(star_surface, BLACK, points, 3)
        
        # Dessiner le remplissage progressif
        if fill_percent > 0:
            fill_points = points[:int(len(points) * min(1, (fill_percent / 100)))]
            if len(fill_points) >= 3:  # Besoin d'au moins 3 points pour un polygone
                pygame.draw.polygon(star_surface, YELLOW, fill_points)
        
        # Dessiner des effets de brillance pour les étoiles remplies
        if fill_percent >= 100 and self.stars_filled:
            for j in range(4):
                angle = self.shine_angle * math.pi / 180 + j * math.pi / 2
                # Calculer les points de départ et d'arrivée relatifs au centre de la surface
                shine_start_x = size + size * 0.6 * math.cos(angle)
                shine_start_y = size + size * 0.6 * math.sin(angle)
                shine_end_x = size + size * 1.2 * math.cos(angle)
                shine_end_y = size + size * 1.2 * math.sin(angle)
                
                # Dessiner la ligne brillante
                pygame.draw.line(
                    star_surface,
                    (255, 255, 200, 150),
                    (shine_start_x, shine_start_y),
                    (shine_end_x, shine_end_y),
                    2
                )
        
        # Ajuster l'opacité si nécessaire
        if fill_percent < 100:
            star_surface.set_alpha(max(100, int(fill_percent*2.55)))  # Plus opaque à mesure que l'étoile se remplit
        
        # Blitter la surface transparente sur l'écran
        screen.blit(star_surface, (x - size, y - size-20))
    
    def draw(self):
        # Dessiner le fond de la popup
        pygame.draw.rect(screen, WHITE, (self.popup_x, self.popup_y, self.popup_width, self.popup_height))
        pygame.draw.rect(screen, BLACK, (self.popup_x, self.popup_y, self.popup_width, self.popup_height), 2)
        
        # Dessiner le titre et le score
        title_surface = font_large.render("Dessin achevé !!", True, BLACK)
        screen.blit(title_surface, (self.popup_x + (self.popup_width - title_surface.get_width()) // 2, self.popup_y + 30))
        
        score_surface = font_large.render(f"Score: {self.score}%", True, BLACK)
        screen.blit(score_surface, (self.popup_x + (self.popup_width - score_surface.get_width()) // 2, self.popup_y + 80))
        
        # Dessiner les étoiles
        star_size = 40
        star_spacing = 120
        start_x = self.popup_x + (self.popup_width - star_spacing * 2) // 2 - 20
        star_y = self.popup_y + 180
        
        # Dessiner les étoiles avec leur animation
        for i in range(3):
            percentage_text = font_medium.render(f"{30 + i * 20}%", True, BLACK)
            screen.blit(percentage_text, (start_x + i * star_spacing - percentage_text.get_width()//2 + star_size//2, star_y + star_size + 10))
            
            self.draw_star(start_x + i * star_spacing + star_size//2, star_y + star_size//2, 
                          star_size, self.stars_fill[i], self.star_jump[i], self.star_rotation[i])
        
        # Afficher les petites étoiles en haut à droite
        try:
            star_icon = pygame.image.load("assets/icon_star.png")
            star_icon = pygame.transform.scale(star_icon, (40, 40))
            screen.blit(star_icon, (self.popup_x + self.popup_width - 110, self.popup_y + 18))
        except:
            # Dessiner une étoile simple si l'image n'est pas disponible
            self.draw_star(self.popup_x + self.popup_width - 90, self.popup_y + 30, 20, 100)
            
        text_x35 = font_medium.render("X35", True, BLACK)
        screen.blit(text_x35, (self.popup_x + self.popup_width - 65, self.popup_y + 25))
        
        # Dessiner les images à droite
        image_x = self.popup_x + self.popup_width + 20
        image_y = self.popup_y + 30
        image_spacing = 20
        
        screen.blit(self.images[0], (image_x, image_y))
        
        # Flèche entre les images
# Flèche entre les images (inversée mais dans la même zone)
        arrow_points = [
            (image_x + 125, image_y + 190 - 10),  # Point en haut
            (image_x + 145, image_y + 190 - 30),  # Coin bas gauche
            (image_x + 105, image_y + 190 - 30)   # Coin bas droit
        ]
        pygame.draw.polygon(screen, GRAY, arrow_points)
        
        screen.blit(self.images[1], (image_x, image_y + 150 + 50))
        
        # Dessiner toutes les particules
        self.particles.draw(screen)

def main():
    clock = pygame.time.Clock()
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((230, 230, 230))
    draw_background(background)
    
    # Score à afficher (à modifier selon vos besoins)
    score = 69
    popup = PopupAnimation(score)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    # Recréer la popup avec un nouveau score pour tester
                    score = random.randint(30, 100)
                    popup = PopupAnimation(score)
        
        screen.blit(background, (0, 0))
        

        
        popup.update()
        popup.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()