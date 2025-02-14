import json
import random
import pygame
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def phrases_similaires(phrase1, phrase2):
    if not phrase1 or not phrase2:
        return 0.0
    emb1 = model.encode(phrase1, convert_to_tensor=True)
    emb2 = model.encode(phrase2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2).item()
    return round(score * 100, 2)

with open("Max/phrases_droles_v2.json") as f:
    data = json.load(f)

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

font = pygame.font.SysFont("Arial", 24)

current_phrase = random.choice(data)
button_rect = pygame.Rect(500, 400, 200, 50)

phrase2 = ""
input_active = False
similarity_score = 0.0

while running:
    screen.fill("white")

    txtsurf = font.render(current_phrase, True, "black")
    screen.blit(txtsurf, (640 - txtsurf.get_width() // 2, 300))

    pygame.draw.rect(screen, "gray", button_rect)
    btn_text = font.render("Changer", True, "black")
    screen.blit(btn_text, (button_rect.x + 50, button_rect.y + 10))

    input_rect = pygame.Rect(400, 500, 480, 40)
    pygame.draw.rect(screen, "black" if input_active else "gray", input_rect, 2)
    
    user_text = font.render(phrase2, True, "black")
    screen.blit(user_text, (input_rect.x + 10, input_rect.y + 10))

    similarity_text = font.render(f"Correspondance: {similarity_score}%", True, "blue")
    screen.blit(similarity_text, (640 - similarity_text.get_width() // 2, 550))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                current_phrase = random.choice(data)
                similarity_score = phrases_similaires(current_phrase, phrase2)
            if input_rect.collidepoint(event.pos):
                input_active = True
            else:
                input_active = False
        if event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_BACKSPACE:
                    phrase2 = phrase2[:-1]
                else:
                    phrase2 += event.unicode
                similarity_score = phrases_similaires(current_phrase, phrase2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
