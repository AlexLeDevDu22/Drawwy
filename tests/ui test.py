import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Définition des murs, sol et plafond
vertices = [
    (-5, -2, -5), (5, -2, -5), (5, -2, 5), (-5, -2, 5),  # Sol
    (-5, 3, -5), (5, 3, -5), (5, 3, 5), (-5, 3, 5)  # Plafond
]
edges = [(0,1), (1,2), (2,3), (3,0),  # Sol
         (4,5), (5,6), (6,7), (7,4),  # Plafond
         (0,4), (1,5), (2,6), (3,7)]  # Murs verticaux

# Fonction pour dessiner la salle
def draw_room():
    glBegin(GL_QUADS)
    
    # Sol
    glColor3f(0.6, 0.6, 0.6)
    glVertex3f(-5, -2, -5)
    glVertex3f(5, -2, -5)
    glVertex3f(5, -2, 5)
    glVertex3f(-5, -2, 5)
    
    # Plafond
    glColor3f(0.8, 0.8, 0.8)
    glVertex3f(-5, 3, -5)
    glVertex3f(5, 3, -5)
    glVertex3f(5, 3, 5)
    glVertex3f(-5, 3, 5)

    # Murs
    glColor3f(0.7, 0.5, 0.3)
    for i in range(4):
        glVertex3fv(vertices[i])
        glVertex3fv(vertices[(i+1)%4])
        glVertex3fv(vertices[(i+1)%4 + 4])
        glVertex3fv(vertices[i + 4])

    glEnd()

# Fonction pour dessiner un tableau (mur du fond)
def draw_painting():
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glVertex3f(-1, 1, -4.9)
    glVertex3f(1, 1, -4.9)
    glVertex3f(1, -1, -4.9)
    glVertex3f(-1, -1, -4.9)
    glEnd()

# Initialisation de Pygame et OpenGL
pygame.init()
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
gluPerspective(60, (800/600), 0.1, 50.0)
glTranslatef(0, 0, -10)

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[K_LEFT]:
        glRotatef(2, 0, 1, 0)
    if keys[K_RIGHT]:
        glRotatef(-2, 0, 1, 0)
    if keys[K_UP]:
        glTranslatef(0, 0, 0.2)
    if keys[K_DOWN]:
        glTranslatef(0, 0, -0.2)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_room()
    draw_painting()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
