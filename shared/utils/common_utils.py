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
            save_data("PLAYER_DATA")
            self.popup_active=True
            self.start_time = pygame.time.get_ticks()
    
    def draw_popup_if_active(self, screen):
        if self.popup_active:
            if self.start_time+5000 < pygame.time.get_ticks():
                self.popup_active=False
            anim_offset=0

            if self.start_time+4000 > pygame.time.get_ticks():
                anim_offset=(self.width+50)*min((pygame.time.get_ticks()-self.start_time)/1000, 1)-(self.width+50)
            else:
                anim_offset=(self.width+50)*max((self.start_time+5000-pygame.time.get_ticks())/1000, 0)-(self.width+50)

            box_rect_achievement = pygame.Rect(50+anim_offset,self.H-230,self.width,self.height)
            pygame.draw.rect(screen,PASTEL_GREEN,box_rect_achievement,border_radius=15)
            #rond valide
            pygame.draw.circle(screen, DARK_BLUE, 
                                    ( 100+anim_offset, self.H-240+ self.height // 2), 
                                    20)
            pygame.draw.line(screen, WHITE, 
                                ( 90+anim_offset, self.H-240 + self.height // 2), 
                                ( 100+anim_offset, self.H-240 + self.height // 2 + 10), 
                                4)
            pygame.draw.line(screen, WHITE, 
                                ( 100+anim_offset, self.H-240 + self.height // 2 + 10), 
                                ( 115+anim_offset, self.H-240 + self.height // 2 - 10), 
                                4)

            #dessiner le texte
            draw_text(self.current_achievement["title"],SMALL_FONT,BLACK,screen, 50+anim_offset + self.width // 2, self.H-245 + self.height // 2)
            draw_text(self.current_achievement["explication"],SMALL_FONT,ORANGE,screen, 50+anim_offset + self.width // 2, self.H-205 + self.height // 2)