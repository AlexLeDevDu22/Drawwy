import pygame
import sys

pygame.init()

width, height = 800, 600
margin = 50
draw_area = pygame.Rect(margin, margin, width - 2 * margin, height - 2 * margin)

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dessiner avec la souris")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

drawing = False
last_pos = None
current_color = BLUE

file = open("pixels.txt", "w")

def draw_line(start, end):
    if draw_area.collidepoint(start) and draw_area.collidepoint(end):
        pygame.draw.line(screen, current_color, start, end, 3)


def draw_background():
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, draw_area, 5)

draw_background()
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if draw_area.collidepoint(event.pos):
                drawing = True
                last_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
        elif event.type == pygame.MOUSEMOTION and drawing:
            current_pos = pygame.mouse.get_pos()
            draw_line(last_pos, current_pos)
            last_pos = current_pos
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                current_color = RED
            elif event.key == pygame.K_g:
                current_color = GREEN
            elif event.key == pygame.K_b:
                current_color = BLUE
            elif event.key == pygame.K_c:
                draw_background()
                pygame.display.flip()

    pygame.display.flip()

file.close()
pygame.quit()
sys.exit()
