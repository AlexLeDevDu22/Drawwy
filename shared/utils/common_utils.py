from shared.ui.common_ui import *
from shared.utils.data_manager import *

import pygame

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

class AchievementManager:

    def __init__(self, W, H):
        #dessiner la boite
        self.width = 500
        self.height = 100
        self.W=W
        self.H=H
        self.popup_active=False
        self.start_time=pygame.time.get_ticks()

    def new_achievement(self, index):
        self.current_achievement=PLAYER_DATA["achievements"][index]
        if not self.current_achievement["succeed"]:
            PLAYER_DATA["achievements"][index]["succeed"]=True
            save_data()
            self.popup_active=True
            self.start_time = pygame.time.get_ticks()
    
    def draw_popup_if_active(self, screen):
        if self.start_time and self.start_time+3000 < pygame.time.get_ticks():
            self.popup_active=False
        if self.popup_active:
            anim_offset=0

            if self.start_time+4000 > pygame.time.get_ticks():
                anim_offset=(self.width+100)*min((self.start_time+1000-pygame.time.get_ticks(), 1000)/1000, 1)
            else:
                anim_offset=(self.width+100)*max((self.start_time+4000-pygame.time.get_ticks())/1000, 0)

            box_rect_achievement = pygame.Rect(anim_offset-50,self.H-230,self.width,self.height)
            pygame.draw.rect(screen,PASTEL_GREEN,box_rect_achievement,border_radius=15)
            #rond valide
            pygame.draw.circle(screen, DARK_BLUE, 
                                    ( anim_offset, self.H-230+ self.height // 2), 
                                    20)
            pygame.draw.line(screen, WHITE, 
                                ( anim_offset-10, self.H-230 + self.height // 2), 
                                ( anim_offset, self.H-230 + self.height // 2 + 10), 
                                4)
            pygame.draw.line(screen, WHITE, 
                                ( anim_offset, self.H-230 + self.height // 2 + 10), 
                                ( anim_offset+15, self.H-230 + self.height // 2 - 10), 
                                4)

            #dessiner le texte
            draw_text(self.current_achievement["title"],SMALL_FONT,BLACK,screen,anim_offset-50 + self.width // 2, self.H-230 + self.height // 2)
            draw_text(self.current_achievement["explication"],SMALL_FONT,LIGHT_GRAY,screen,anim_offset-50 + self.width // 2, self.H-200 + self.height // 2)