from shared.common_ui import *
from MultiGame.ui.widgets import *
import MultiGame.utils.connection as connection

import threading
import pygame
import yaml
import MultiGame.utils.tools as tools
import asyncio
import os
from datetime import datetime, timedelta

with open("assets/config.yaml", "r") as f:
    config = yaml.safe_load(f)

class MultiGame:
    
    def __init__(self,screen,clock, W,H):
        if not tools.is_connected():
            print( "Désolé, une connexion internet est requise.")
            return
        
        self.screen, self.W, self.H=screen, W,H
        self.connected=False
        self.server=None

        self.PLAYER_ID=0
        self.PLAYERS=[]
        self.CURRENT_DRAWER=0
        self.CURRENT_SENTENCE=""
        self.MESSAGES=[]
        self.CANVAS=None
        self.ALL_FRAMES=[]
        self.STEP_NUM=0
        self.ROLL_BACK=0
        self.SIO=None
        self.GAMESTART=None
    
        try:
            self.connection_loop=asyncio.new_event_loop()
            self.connexion_thread=threading.Thread(target=connection.start_connexion, args=(self,))
            self.connexion_thread.start()

            self.game_remaining_time=config["game_duration"]
            
            self.me={   "id": -1,
                        "pseudo": "",
                        "points": 0,
                        "found":False,
                        "is_drawer":False
                        }
            
            #pen values
            self.pen_color=(0,0,0)
            self.pen_radius=6
            self.mouseDown=False
            self.lastMouseDown=False
            self.last_canvas_click=None
            
            self.mouse_pos=(0,0)
            
            #for drawing
            self.second_draw_frames=[]
            
            self.frame_num=0
            
            self.guess_input_active=False
            self.guess=""

            self.PLAYERS=[]
            
            while 1:
                clock.tick(config["game_page_fps"])

                for player in self.PLAYERS:
                    if player["id"] == self.PLAYER_ID:
                        self.me=player
                        self.me["is_drawer"]=self.PLAYER_ID==self.CURRENT_DRAWER
                        break

                if self.frame_num%2==0:
                    self.game_remaining_time=max(0, (self.GAMESTART+timedelta(seconds=config["game_duration"])-datetime.now()).seconds%config["game_duration"] if self.GAMESTART else config["game_duration"])

                    if self.game_remaining_time==0: #if game time over
                        if self.me["is_drawer"]:
                            tools.emit_sio(self.sio, "game_finished", None)
                        self.GAMESTART=datetime.now()
                
                self.events=pygame.event.get()
                
                self.screen.fill(BEIGE)

                players(self)
                sentence(self)
                drawing(self)
                chat(self)
                if self.me["id"]==self.PLAYER_ID:
                    couleurs(self)
                    slider_radius(self)
                timer(self)

                if not self.connected:
                    font = pygame.font.Font("assets/PermanentMarker.ttf", 20)
                    text = font.render("Connexion au serveur...", True, (0, 0, 0))
                    self.screen.blit(text, text.get_rect(center=(self.W // 2 + 5, self.H // 2 -100)))
                
                for event in self.events:
                    if (event.type == pygame.KEYDOWN and event.key == pygame.K_q and not self.guess_input_active) or event.type == pygame.QUIT:
                        threading.Thread(target=self.disconnect, daemon=True).start()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.mouseDown=True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.mouseDown=False
                        self.last_canvas_click=None
                    if event.type == pygame.MOUSEMOTION:
                        self.mouse_pos=event.pos
                        if self.mouseDown:
                            self.lastMouseDown=self.mouseDown
                    if event.type == pygame.VIDEORESIZE:
                        self.W, self.H = tools.get_screen_size()
                
                pygame.display.flip()
                
                self.frame_num=(self.frame_num+1)%config["game_page_fps"]

        except KeyboardInterrupt:
            self.disconnect()
            os._exit(0)
