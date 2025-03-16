from shared.ui.common_ui import *
from MultiGame.ui.widgets import *
from shared.ui.elements import ColorPicker
import MultiGame.utils.connection as connection

import threading
import pygame
import yaml
import MultiGame.utils.tools as tools
import asyncio
import os
from datetime import datetime, timedelta

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

class MultiGame:
    
    def __init__(self,screen,clock, W,H):
        if not tools.is_connected():
            print( "Désolé, une connexion internet est requise.")
            return
        
        pygame.display.set_caption(f"Drawwy - Mode Multijoueur")
        
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
            self.mouse_down=False
            self.lastMouseDown=False
            self.last_canvas_click=None

            self.color_picker=ColorPicker(0.81 * self.W, 0.04 * self.H, 0.18 * self.W, 0.25 * self.H)
            
            #for drawing
            self.second_draw_frames=[]
            
            self.frame_num=0
            
            self.guess_input_active=False
            self.guess=""

            self.PLAYERS=[]
            
            while 1:
                clock.tick(config["fps"])

                self.mouse_pos=pygame.mouse.get_pos()

                for i in range(len(self.PLAYERS)):
                    if self.PLAYERS[i]["id"] == self.PLAYER_ID:
                        print(self.PLAYER_ID,self.CURRENT_DRAWER)
                        self.me=self.PLAYERS[i]
                        self.me["is_drawer"]=self.PLAYER_ID==self.CURRENT_DRAWER
                        break
                    
                if self.frame_num%2==0:
                    self.game_remaining_time=max(0, (self.GAMESTART+timedelta(seconds=config["game_duration"])-datetime.now()).seconds%config["game_duration"] if self.GAMESTART else config["game_duration"])

                    if self.game_remaining_time==0: #if game time over
                        if self.me["is_drawer"]:
                            tools.emit_sio(self.SIO, "game_finished", None)
                        self.GAMESTART=datetime.now()
                
                self.events=pygame.event.get()
                
                self.screen.fill(BEIGE)

                players(self)
                sentence(self)
                drawing(self)
                chat(self)
                if self.me["is_drawer"]:
                    #couleurs(self)
                    if self.mouse_down:
                        color=self.color_picker.get_color_at(self.mouse_pos)
                        if color:
                            self.pen_color=color
                    self.color_picker.draw(self.screen)
                    slider_radius(self)
                timer(self)

                if not self.connected:
                    font = pygame.font.Font("assets/PermanentMarker.ttf", 20)
                    text = font.render("Connexion au serveur...", True, (0, 0, 0))
                    self.screen.blit(text, text.get_rect(center=(self.W // 2 + 5, self.H // 2 -100)))
                
                for event in self.events:
                    if (event.type == pygame.KEYDOWN and event.key == pygame.K_q and not self.guess_input_active) or event.type == pygame.QUIT:
                        threading.Thread(target=connection.disconnect,args=(self,), daemon=True).start()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.mouse_down=True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.mouse_down=False
                        self.last_canvas_click=None
                    if event.type == pygame.MOUSEMOTION:
                        if self.mouse_down:
                            self.lastMouseDown=self.mouse_down
                    if event.type == pygame.VIDEORESIZE:
                        self.W, self.H = tools.get_screen_size()
                
                pygame.display.flip()
                
                self.frame_num=(self.frame_num+1)%config["fps"]

        except KeyboardInterrupt:
            threading.Thread(target=connection.disconnect,args=(self,), daemon=True).start()
            os._exit(0)
