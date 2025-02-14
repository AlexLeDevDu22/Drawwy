import json
import random
import pygame

with open("phrases_droles_v2.json") as f:
    data = json.load(f)
random.shuffle(data)


pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True


font = pygame.font.SysFont("Arial", 24)


current_phrase = data[0]
button_rect = pygame.Rect(500, 400, 200, 50) 

while running:
    screen.fill("white")

    txtsurf = font.render(current_phrase, True, "black")
    screen.blit(txtsurf, (640 - txtsurf.get_width() // 2, 300))


    pygame.draw.rect(screen, "gray", button_rect)
    btn_text = font.render("Changer", True, "black")
    screen.blit(btn_text, (button_rect.x + 50, button_rect.y + 10))


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):  
                current_phrase = random.choice(data)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
