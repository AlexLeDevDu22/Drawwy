import pygame
import sys
import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()
ngrok_domain = os.getenv("NGROK_DOMAIN")

# Couleurs
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
BLEU_CLAIR = pygame.Color('lightskyblue3')
BLEU = pygame.Color('dodgerblue2')

async def handle_connection_client(pseudo):
    """Gère la connexion WebSocket avec le serveur"""
    async with websockets.connect("wss://" + ngrok_domain) as websocket:
        await websocket.send(json.dumps({"type": "join", "pseudo": pseudo}))

        async for message in websocket:
            data = json.loads(message)
            print(data)

def get_screen_size():
    """Retourne la taille de l'écran"""
    info_ecran = pygame.display.Info()
    return info_ecran.current_w, info_ecran.current_h

def input_pseudo(screen):
    """Affiche une fenêtre pour entrer le pseudo"""
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(100, 80, 200, 40)
    text = ''
    active = True
    clock = pygame.time.Clock()
    
    while True:
        screen.fill(BLANC)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and text.strip():
                    return text  # Retourne le pseudo saisi
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

        # Mise à jour visuelle
        color = BLEU if active else BLEU_CLAIR
        txt_surface = font.render(text, True, NOIR)
        input_box.w = max(200, txt_surface.get_width() + 10)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

def game_ui(screen):
    """Affiche l'interface de jeu après la connexion"""
    largeur, hauteur = get_screen_size()

    zones = [
        (20/100*largeur, 4.17/100*hauteur, 60/100*largeur, 91/100*hauteur),  # Zone de dessin
        (1/100*largeur, 4.17/100*hauteur, 18/100*largeur, 70/100*hauteur),   # Liste joueurs
        (1/100*largeur, 75/100*hauteur, 18/100*largeur, 20/100*hauteur),    # Mot à deviner
        (81/100*largeur, 4.17/100*hauteur, 18/100*largeur, 91/100*hauteur), # Chat
    ]

    running = True
    while running:
        screen.fill(BLANC)
        for x, y, w, h in zones:
            pygame.draw.rect(screen, NOIR, (x, y, w, h), 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

async def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Entrez votre pseudo")

    # Étape 1 : Demande du pseudo
    pseudo = input_pseudo(screen)

    # Étape 2 : Connexion WebSocket
    await handle_connection_client(pseudo)

    # Étape 3 : Affichage de l'UI du jeu
    largeur, hauteur = get_screen_size()
    screen = pygame.display.set_mode((largeur, hauteur))  # Agrandissement après la connexion
    pygame.display.set_caption("UIdrawer")
    game_ui(screen)

    pygame.quit()

asyncio.run(main())
