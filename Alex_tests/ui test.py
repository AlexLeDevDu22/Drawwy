import pygame
import sys
import asyncio
import json
import websockets
import random
from dotenv import load_dotenv
import os

load_dotenv()
ngrok_domain = os.getenv("NGROK_DOMAIN")

async def handle_connection_client(pseudo):
    async with websockets.connect("wss://"+ngrok_domain) as websocket:
        # Demander un pseudo et s'enregistrer
        
        await websocket.send(json.dumps({"type": "join", "pseudo": pseudo}))

        # Recevoir les mises à jour et dessiner si c'est son tour
        print(websocket)
        async for message in websocket:
            data = json.loads(message)
            
            print(data)
            
            if data["type"] == "welcome":
                print(f"🎮 Connecté avec l'ID {data['id']}")
                print(f"👥 Joueurs actuels : {[p['pseudo'] for p in data['players']]}")
            
            elif data["type"] == "update":
                print(f"📜 Mise à jour : {len(data['players'])} joueurs, Tour : {data['turn']}")
                print(f"🎨 Canvas mis à jour.")

async def main():
    pygame.init()
    width, height = 400, 200
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Entrez votre pseudo")

    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(100, 80, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    text = ''
    active = True
    clock = pygame.time.Clock()

    while True:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    active = False
                    pseudo = text  # Récupère le pseudo une fois la touche "Entrée" pressée

                    break
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode
        
        color = color_active if active else color_inactive
        txt_surface = font.render(text, True, (0, 0, 0))
        width_text = max(200, txt_surface.get_width() + 10)
        input_box.w = width_text
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)


asyncio.run(handle_connection_client(pseudo))

