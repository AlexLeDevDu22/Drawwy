import pygame

def run_drawing_app():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Dessiner avec la souris")

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    screen.fill(WHITE)

    drawing = False
    last_pos = None
    color = BLACK

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                last_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                drawing = False
            elif event.type == pygame.MOUSEMOTION and drawing:
                pygame.draw.line(screen, color, last_pos, event.pos, 3)
                last_pos = event.pos

        pygame.display.flip()

    pygame.quit()

run_drawing_app()
