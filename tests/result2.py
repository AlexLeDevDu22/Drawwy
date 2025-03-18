import pygame
import math
import sys
from pygame.locals import *

# Initialisation
pygame.init()
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Animation de Score")

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

# Police
font_large = pygame.font.SysFont('Arial', 36, bold=True)
font_medium = pygame.font.SysFont('Arial', 24)

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
        
        # Déterminer combien d'étoiles sont remplies
        self.filled_stars = 0
        if score >= 70:
            self.filled_stars = 3
        elif score >= 50:
            self.filled_stars = 2
        elif score >= 30:
            self.filled_stars = 1
    
    def update(self):
        # Animation d'entrée de la popup
        if self.popup_y < self.target_y:
            self.popup_y += self.animation_speed
            if self.popup_y >= self.target_y:
                self.popup_y = self.target_y
                self.animation_done = True
        
        # Animation de remplissage des étoiles
        if self.animation_done and not self.stars_filled:
            all_filled = True
            for i in range(3):
                if i < self.filled_stars:
                    self.stars_fill[i] += self.star_animation_speed
                    if self.stars_fill[i] > 100:
                        self.stars_fill[i] = 100
                    else:
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
    
    def draw_star(self, x, y, size, fill_percent, jump_offset=0, rotation=0):
        print(fill_percent)
        # Créer une surface transparente
        star_surface = pygame.Surface((size * 2, size * 2+20), pygame.SRCALPHA)
        star_surface.set_alpha(fill_percent*2.55)  # Définir l'opacité
        
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
            fill_points = points[:int(len(points) * max(1,(fill_percent / 100)))]
            pygame.draw.polygon(star_surface, YELLOW, fill_points)
        
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
        star_icon = pygame.image.load("assets/icon_star.png")
        star_icon = pygame.transform.scale(star_icon, (40, 40))
        screen.blit(star_icon, (self.popup_x + self.popup_width - 110, self.popup_y + 18))
        text_x35 = font_medium.render("X35", True, BLACK)
        screen.blit(text_x35, (self.popup_x + self.popup_width - 65, self.popup_y + 25))
        
        # Dessiner les images à droite
        image_x = self.popup_x + self.popup_width + 20
        image_y = self.popup_y + 30
        image_spacing = 20
        
        screen.blit(self.images[0], (image_x, image_y))
        
        # Flèche entre les images
        arrow_points = [
            (image_x + 125, image_y + 150 + 10),
            (image_x + 145, image_y + 150 + 30),
            (image_x + 105, image_y + 150 + 30)
        ]
        pygame.draw.polygon(screen, GRAY, arrow_points)
        
        screen.blit(self.images[1], (image_x, image_y + 150 + 50))

def main():
    clock = pygame.time.Clock()
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((230, 230, 230))
    
    # Score à afficher (à modifier selon vos besoins)
    score = 69
    popup = PopupAnimation(score)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        
        screen.blit(background, (0, 0))
        
        popup.update()
        popup.draw()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()