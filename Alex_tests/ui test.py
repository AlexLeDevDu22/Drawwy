import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Dessine avec Pygame")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

drawing = False
start_pos = None
shape = "rectangle"
line_width = 2

actions = []
action_index = -1

screen.fill(WHITE)

font = pygame.font.SysFont(None, 36)

button_rect = pygame.Rect(10, 10, 120, 40)
button_circle = pygame.Rect(140, 10, 120, 40)
button_line = pygame.Rect(270, 10, 120, 40)
button_plus = pygame.Rect(530, 10, 40, 40)
button_minus = pygame.Rect(580, 10, 40, 40)

def draw_buttons():
    pygame.draw.rect(screen, GRAY, button_rect)
    pygame.draw.rect(screen, BLACK, button_rect, 2)
    screen.blit(font.render("Rectangle", True, BLACK), (button_rect.x + 10, button_rect.y + 10))
    
    pygame.draw.rect(screen, GRAY, button_circle)
    pygame.draw.rect(screen, BLACK, button_circle, 2)
    screen.blit(font.render("Cercle", True, BLACK), (button_circle.x + 30, button_circle.y + 10))
    
    pygame.draw.rect(screen, GRAY, button_line)
    pygame.draw.rect(screen, BLACK, button_line, 2)
    screen.blit(font.render("Ligne", True, BLACK), (button_line.x + 35, button_line.y + 10))
    
    pygame.draw.rect(screen, GRAY, button_plus)
    pygame.draw.rect(screen, BLACK, button_plus, 2)
    screen.blit(font.render("+", True, BLACK), (button_plus.x + 10, button_plus.y + 5))
    
    pygame.draw.rect(screen, GRAY, button_minus)
    pygame.draw.rect(screen, BLACK, button_minus, 2)
    screen.blit(font.render("-", True, BLACK), (button_minus.x + 10, button_minus.y + 5))
    
    screen.blit(font.render(f"Épaisseur: {line_width}", True, BLACK), (630, 20))

def redraw_screen():
    screen.fill(WHITE)
    draw_buttons()
    for action in actions[:action_index+1 ]:
        shape_type, start, end, width = action
        if shape_type == "rectangle":
            rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))
            pygame.draw.rect(screen, BLACK, rect, width)
        elif shape_type == "circle":
            radius = int(((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5)
            pygame.draw.circle(screen, RED, start, radius, width)
        elif shape_type == "line":
            pygame.draw.line(screen, BLUE, start, end, width)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                shape = "rectangle"
            elif button_circle.collidepoint(event.pos):
                shape = "circle"
            elif button_line.collidepoint(event.pos):
                shape = "line"
            elif button_plus.collidepoint(event.pos):
                line_width = min(20, line_width + 1)
            elif button_minus.collidepoint(event.pos):
                line_width = max(1, line_width - 1)
            else:
                drawing = True
                start_pos = event.pos
        
        if event.type == pygame.MOUSEMOTION:
            if drawing:
                redraw_screen()
                end_pos = event.pos
                if shape == "rectangle":
                    x = min(start_pos[0], end_pos[0])
                    y = min(start_pos[1], end_pos[1])
                    width = abs(end_pos[0] - start_pos[0])
                    height = abs(end_pos[1] - start_pos[1])
                    rect = pygame.Rect(x, y, width, height)
                    pygame.draw.rect(screen, BLACK, rect, line_width)
                elif shape == "circle":
                    radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                    pygame.draw.circle(screen, RED, start_pos, radius, line_width)
                elif shape == "line":
                    pygame.draw.line(screen, BLUE, start_pos, end_pos, line_width)
        
        if event.type == pygame.MOUSEBUTTONUP:
            if drawing:
                drawing = False
                end_pos = event.pos
                # Normalisation des coordonnées pour enregistrer l'action
                if shape == "rectangle":
                    x = min(start_pos[0], end_pos[0])
                    y = min(start_pos[1], end_pos[1])
                    width = abs(end_pos[0] - start_pos[0])
                    height = abs(end_pos[1] - start_pos[1])
                    actions.append(("rectangle", (x, y), (x + width, y + height), line_width))
                elif shape == "circle":
                    radius = int(((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2) ** 0.5)
                    actions.append(("circle", start_pos, end_pos, line_width))
                elif shape == "line":
                    actions.append(("line", start_pos, end_pos, line_width))
                action_index2 += 1
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if action_index >= 0:
                    action_index2 = action_index
                    action_index-=1
                    
                    # Réinitialiser le dessin en cours si nécessaire
                    drawing = False
                    start_pos = None
                    pygame.time.delay(50)  # Ajouter un délai pour stabiliser l'affichage
                    redraw_screen()
            if event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if action_index < len(actions) - 1:
                    action_index2 = action_index+1
                    pygame.time.delay(50)  # Ajouter un délai pour stabiliser l'affichage
                    redraw_screen()
            

    draw_buttons()
    pygame.display.flip()
