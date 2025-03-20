import pygame
import math

nb_petals = 10
taille_level = 30
radius_ratio = 0.15

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
font = pygame.font.Font(None, max(30, taille_level))

x_center = width // 2
y_center = height // 3
radius = int(width * radius_ratio)

petals = []


def draw_flower():
    screen.fill((255, 255, 255))
    petals.clear()

    for i in range(nb_petals):
        angle = (2 * math.pi / nb_petals) * i
        x = int(x_center + radius * math.cos(angle))
        y = int(y_center + radius * math.sin(angle))

        pygame.draw.circle(screen, (255, 0, 0), (x, y), taille_level)
        text = font.render(str(i + 1), True, (255, 255, 255))
        text_rect = text.get_rect(center=(x, y))
        screen.blit(text, text_rect)

        petals.append((x, y, taille_level))


draw_flower()
pygame.display.update()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, (x, y, r) in enumerate(petals):
                if math.hypot(mx - x, my - y) <= r:
                    print(f"Pétale {i + 1} cliqué !")

pygame.quit()
