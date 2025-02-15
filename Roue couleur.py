import pygame
import sys
import tools
import gameVar
import yaml
import tools
import math 
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

#*pygame
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
BLEU_CLAIR = pygame.Color('lightskyblue3')
BLEU = pygame.Color('dodgerblue2')
BEIGE = (250, 240, 230)
VERT = (0,255,0)
ROUGE= (255,0,0)
JAUNE=(255,255,0)
MAGENTA=(255,0,255)
CYAN=(0,255,255)



# Initialisation de Pygame
pygame.init()
tools.get_screen_size()
ecran = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cercle chromatique")

# Centre et rayon du cercle
center = (width // 2, height // 2)
radius = 200

# Nombre de divisions (plus il y en a, plus le dégradé est fluide)
num_sections = 36  # Ajustable

running = True
while running:
    ecran.fill((255, 255, 255))  # Fond blanc

    # Dessiner les arcs colorés
    for i in range(num_sections):
        angle_start = (i / num_sections) * 2 * math.pi  # Début de l'arc
        angle_end = ((i + 1) / num_sections) * 2 * math.pi  # Fin de l'arc
        
        # Générer une couleur en fonction de l'angle
        hue = i / num_sections  # Valeur de teinte entre 0 et 1
        color = pygame.Color(0)  # Créer une couleur vide
        color.hsva = (hue * 360, 100, 100, 100)  # Teinte, saturation, valeur, alpha

        # Points pour dessiner un arc
        points = []
        for j in range(10):  # Plus de points = plus lisse
            angle = angle_start + (angle_end - angle_start) * (j / 9)
            x = center[0] + math.cos(angle) * radius
            y = center[1] + math.sin(angle) * radius
            points.append((x, y))
        
        # Fermer l'arc en reliant au centre
        points.append(center)

        # Dessiner le segment coloré
        pygame.draw.polygon(ecran, color, points)

    pygame.display.flip()

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
pages.__init__(self)


def couleurs(self):
    num_sections = 36
    running = True
    center_x, center_y = 0.2 * self.W, 0.04 * self.H
    radius = 100
    # Dessiner les arcs colorés
    for i in range(num_sections):
        angle_start = (i / num_sections) * 2 * math.pi  # Début de l'arc
        angle_end = ((i + 1) / num_sections) * 2 * math.pi  # Fin de l'arc

        # Générer une couleur en fonction de l'angle
        hue = i / num_sections  # Valeur de teinte entre 0 et 1
        color = pygame.Color(0)
        color.hsva = (hue * 360, 100, 100, 100)  # Teinte, saturation, valeur, alpha

            # Points pour dessiner un arc
        points = []
        for j in range(10):  # Plus de points = plus lisse
            angle = angle_start + (angle_end - angle_start) * (j / 9)
            x = center_x + math.cos(angle) * radius  # Décalé au bon endroit
            y = center_y + math.sin(angle) * radius
            points.append((x, y))
            
            # Fermer l'arc en reliant au centre
        points.append((center_x, center_y))

            # Dessiner le segment coloré
        pygame.draw.polygon(self.screen, color, points)