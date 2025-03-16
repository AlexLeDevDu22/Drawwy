import pygame
import sys
import math
import random
import time
from pygame import gfxdraw
from elements import Button, FloatingObject

# Initialisation de Pygame
pygame.init()
pygame.font.init()

# Constantes
WIDTH, HEIGHT = 1280, 720
TITLE = "Drawwy - Résultats"
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (130, 94, 196)
LIGHT_PURPLE = (157, 127, 211)
DARK_PURPLE = (103, 72, 158)
PINK = (255, 130, 186)
YELLOW = (255, 223, 97)
BLUE = (97, 190, 255)
GREEN = (97, 255, 162)
LIGHT_BLUE = (119, 181, 254)
VERY_LIGHT_BLUE = (160, 205, 255)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
RED = (255, 90, 90)

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
except:
    print("Erreur lors du chargement des polices. Utilisation des polices par défaut.")
    title_font = pygame.font.SysFont('Arial', 120)
    subtitle_font = pygame.font.SysFont('Arial', 70)
    theme_font = pygame.font.SysFont('Arial', 50)
    button_font = pygame.font.SysFont('Arial', 40)
    info_font = pygame.font.SysFont('Arial', 30)

def draw_background(surface):
    # Dégradé de fond bleu clair
    for y in range(HEIGHT):
        # Interpolation entre deux couleurs pour créer un dégradé
        color = [
            int(LIGHT_BLUE[i] + (VERY_LIGHT_BLUE[i] - LIGHT_BLUE[i]) * (y / HEIGHT))
            for i in range(3)
        ]
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))

class StarRating:
    def __init__(self, x, y, width, height, num_stars=3, score=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.num_stars = num_stars
        self.score = score  # Entre 0 et num_stars
        self.animation_progress = 0
        self.star_scale = 1.0
        self.particles = []
        self.shine_angle = 0
        self.completed_stars = 0
        self.start_time = time.time()
        self.delay_per_star = 0.5  # Secondes entre chaque étoile
        
    def update(self):
        current_time = time.time() - self.start_time
        
        # Calculer combien d'étoiles devraient être affichées à l'instant présent
        should_show_stars = min(self.score, int(current_time / self.delay_per_star) + 1)
        
        # Si une nouvelle étoile doit apparaître
        if should_show_stars > self.completed_stars and self.completed_stars < self.num_stars:
            # Ajouter des particules pour l'animation
            self.add_star_particles(self.completed_stars)
            self.completed_stars = should_show_stars
        
        # Mettre à jour les particules
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vy'] += 0.05  # Légère gravité
        
        # Supprimer les particules expirées
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # Animation d'étoile
        self.animation_progress += 0.03
        if self.animation_progress > math.pi * 2:
            self.animation_progress = 0
        
        self.star_scale = 1.0 + 0.1 * math.sin(self.animation_progress)
        
        # Rotation de l'effet brillant
        self.shine_angle = (self.shine_angle + 1) % 360
    
    def add_star_particles(self, star_index):
        star_x = self.rect.x + (star_index + 0.5) * (self.rect.width // self.num_stars)
        star_y = self.rect.centery
        
        # Créer une explosion de particules
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            size = random.uniform(2, 6)
            life = random.uniform(30, 60)
            self.particles.append({
                'x': star_x,
                'y': star_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'life': life,
                'color': GOLD
            })
    
    def draw(self, surface):
        # Dessiner les particules
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 60))
            particle_color = (*particle['color'], alpha)
            gfxdraw.filled_circle(
                surface, 
                int(particle['x']), 
                int(particle['y']), 
                int(particle['size']), 
                particle_color
            )
        
        # Dessiner les étoiles
        star_width = self.rect.width // self.num_stars
        
        for i in range(self.num_stars):
            star_x = self.rect.x + (i + 0.5) * star_width
            star_y = self.rect.centery
            
            # Déterminer si l'étoile est complétée
            is_completed = i < self.completed_stars
            
            # Si c'est l'étoile active en cours d'animation
            is_active = i == self.completed_stars - 1
            
            # Dessiner l'étoile
            if is_completed:
                star_color = GOLD
                
                # Appliquer une échelle spéciale pour l'étoile active
                scale = self.star_scale if is_active else 1.0
                
                # Dessiner l'effet de brillance pour les étoiles complétées
                if is_active:
                    for j in range(8):
                        angle = self.shine_angle * math.pi / 180 + j * math.pi / 4
                        shine_x = star_x + math.cos(angle) * 40 * scale
                        shine_y = star_y + math.sin(angle) * 40 * scale
                        pygame.draw.line(
                            surface, 
                            (255, 255, 200, 100),
                            (star_x, star_y),
                            (shine_x, shine_y),
                            2
                        )
            else:
                star_color = SILVER
                scale = 1.0
            
            # Dessiner l'étoile
            self.draw_star(surface, star_x, star_y, 25 * scale, star_color)
    
    def draw_star(self, surface, x, y, size, color):
        # Dessiner une étoile à 5 branches
        points = []
        for i in range(10):
            # Angle pour chaque point
            angle = math.pi / 2 + i * 2 * math.pi / 10
            # Rayon alterne entre taille externe et interne
            radius = size if i % 2 == 0 else size / 2.5
            # Calculer les coordonnées
            point_x = x + radius * math.cos(angle)
            point_y = y + radius * math.sin(angle)
            points.append((point_x, point_y))
        
        # Dessiner l'étoile remplie
        pygame.draw.polygon(surface, color, points)
        # Dessiner le contour
        pygame.draw.polygon(surface, BLACK, points, 2)

class CompareDraw:
    def __init__(self, x, y, width, height, original_image, player_drawing):
        self.rect = pygame.Rect(x, y, width, height)
        self.original_image = original_image
        self.player_drawing = player_drawing
        self.animation_progress = 0
        self.show_original = True
        self.fade_timer = 0
        self.comparison_lines = []
        self.generate_comparison_lines()
    
    def generate_comparison_lines(self):
        # Générer des lignes pour l'effet visuel de comparaison
        # Ces lignes connectent des points correspondants entre les deux images
        num_lines = 15
        for _ in range(num_lines):
            # Points aléatoires sur les images
            x1 = random.randint(0, self.original_image.get_width())
            y1 = random.randint(0, self.original_image.get_height())
            
            # Point correspondant sur le dessin du joueur (avec un léger décalage pour l'effet)
            offset = 20
            x2 = max(0, min(self.original_image.get_width(), x1 + random.randint(-offset, offset)))
            y2 = max(0, min(self.original_image.get_height(), y1 + random.randint(-offset, offset)))
            
            # Ajouter la ligne
            self.comparison_lines.append({
                'start': (x1, y1),
                'end': (x2, y2),
                'color': random.choice([BLUE, GREEN, YELLOW, PINK]),
                'width': random.randint(1, 3),
                'alpha': 0,
                'fade_in': random.uniform(0.01, 0.03)
            })
    
    def update(self):
        # Mettre à jour l'animation de fondu entre les images
        self.fade_timer += 1
        if self.fade_timer >= 180:  # Changer toutes les 3 secondes
            self.fade_timer = 0
            self.show_original = not self.show_original
        
        # Calculer la progression du fondu
        if self.fade_timer < 60:
            self.animation_progress = self.fade_timer / 60
        else:
            self.animation_progress = 1.0
        
        # Mettre à jour les lignes de comparaison
        for line in self.comparison_lines:
            if self.show_original:
                line['alpha'] = max(0, line['alpha'] - line['fade_in'] * 2)
            else:
                line['alpha'] = min(1, line['alpha'] + line['fade_in'])
    
    def draw(self, surface):
        # Dessiner le cadre
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=15)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=15)
        
        # Marges intérieures
        inner_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 10,
            self.rect.width - 20,
            self.rect.height - 20
        )
        
        # Redimensionner les images pour les adapter au cadre
        scaled_original = pygame.transform.scale(self.original_image, (inner_rect.width, inner_rect.height))
        scaled_player = pygame.transform.scale(self.player_drawing, (inner_rect.width, inner_rect.height))
        
        # Dessiner l'image selon l'état d'animation
        if self.show_original:
            if self.animation_progress < 1.0:
                # Fondu entre le dessin du joueur et l'original
                surface.blit(scaled_player, inner_rect)
                temp_surface = scaled_original.copy()
                temp_surface.set_alpha(int(255 * self.animation_progress))
                surface.blit(temp_surface, inner_rect)
            else:
                # Afficher l'original complètement
                surface.blit(scaled_original, inner_rect)
        else:
            if self.animation_progress < 1.0:
                # Fondu entre l'original et le dessin du joueur
                surface.blit(scaled_original, inner_rect)
                temp_surface = scaled_player.copy()
                temp_surface.set_alpha(int(255 * self.animation_progress))
                surface.blit(temp_surface, inner_rect)
            else:
                # Afficher le dessin du joueur complètement
                surface.blit(scaled_player, inner_rect)
        
        # Dessiner les lignes de comparaison quand on montre le dessin du joueur
        if not self.show_original:
            for line in self.comparison_lines:
                if line['alpha'] > 0:
                    # Ajuster les coordonnées aux coordonnées du cadre
                    start_x = inner_rect.x + line['start'][0] * inner_rect.width / self.original_image.get_width()
                    start_y = inner_rect.y + line['start'][1] * inner_rect.height / self.original_image.get_height()
                    end_x = inner_rect.x + line['end'][0] * inner_rect.width / self.original_image.get_width()
                    end_y = inner_rect.y + line['end'][1] * inner_rect.height / self.original_image.get_height()
                    
                    # Créer une couleur avec alpha
                    color_with_alpha = (*line['color'], int(255 * line['alpha']))
                    
                    # Dessiner la ligne
                    pygame.draw.line(
                        surface,
                        color_with_alpha,
                        (start_x, start_y),
                        (end_x, end_y),
                        line['width']
                    )
        
        # Ajouter une étiquette pour indiquer quelle image est affichée
        label_text = "Original" if self.show_original else "Votre Dessin"
        label_color = BLUE if self.show_original else GREEN
        label = info_font.render(label_text, True, label_color)
        label_rect = label.get_rect(center=(self.rect.centerx, self.rect.bottom + 30))
        surface.blit(label, label_rect)

class Confetti:
    def __init__(self):
        self.particles = []
        self.active = False

    def start(self):
        self.active = True
        self.particles = []

        # Créer des confettis
        for _ in range(200):
            x = random.randint(0, WIDTH)
            y = random.randint(-HEIGHT, 0)
            speed = random.uniform(2, 5)
            size = random.randint(5, 15)
            color = random.choice([RED, YELLOW, GREEN, BLUE, PINK])
            self.particles.append({'x': x, 'y': y, 'speed': speed, 'size': size, 'color': color})

    def update(self):
        if not self.active:
            return
        
        for particle in self.particles:
            particle['y'] += particle['speed']
            particle['x'] += math.sin(particle['y'] * 0.05) * 2  # Effet de flottement
        
        # Retirer les confettis qui sortent de l'écran
        self.particles = [p for p in self.particles if p['y'] < HEIGHT]

    def draw(self, surface):
        for particle in self.particles:
            pygame.draw.circle(surface, particle['color'], (int(particle['x']), int(particle['y'])), particle['size'])

original_image = pygame.image.load("tests/model.png")
player_drawing = pygame.image.load("tests/model.png")

# Initialisation des objets
confetti = Confetti()
star_rating = StarRating(WIDTH // 2 - 150, HEIGHT // 3, 300, 100, score=2)
compare_draw = CompareDraw(WIDTH // 4, HEIGHT // 2 - 150, 300, 300, original_image, player_drawing)

# Boutons
buttons = [
    Button(WIDTH // 2 - 400, HEIGHT - 100, text="Rejouer"),
    Button(WIDTH // 2-100, HEIGHT - 100, text="Réesayer"),
    Button(WIDTH // 2 + 320, HEIGHT - 100, text="Quitter")
]

# Lancer les confettis si le joueur a au moins une étoile
if star_rating.score > 0:
    confetti.start()

# Boucle principale
running = True
while running:
    screen.fill(WHITE)
    draw_background(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Mise à jour des animations
    star_rating.update()
    compare_draw.update()
    confetti.update()
    
    # Dessin des éléments
    compare_draw.draw(screen)
    star_rating.draw(screen)
    confetti.draw(screen)

    # Dessin des boutons
    for button in buttons:
        button.check_hover(pygame.mouse.get_pos())
        button.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
