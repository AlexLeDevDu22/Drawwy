from shared.ui.common_ui import *

import pygame

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

class achievement_popup:

    def __init__(self, text,description,H,W,surface):
        #dessiner la boite
        self.width = 500
        self.height = 100
        self.W=W
        self.H=H
        self.surface=surface
        self.text = text
        self.description = description
        self.active=False
        self.start_time=None
    
    def start(self):
        self.active=True
        self.start_time = pygame.time.get_ticks()

    def draw_if_active(self):
        if self.start_time and self.start_time+3000 < pygame.time.get_ticks():
            self.active=False
            self.start_time=None
        if self.active:
            box_rect_achievement = pygame.Rect(50,self.H-230,self.width,self.height)
            pygame.draw.rect(self.surface,PASTEL_GREEN,box_rect_achievement,border_radius=15)
            #rond valide
            pygame.draw.circle(self.surface, DARK_BLUE, 
                                    ( 100, self.H-165+ self.height // 2), 
                                    20)
            pygame.draw.line(self.surface, WHITE, 
                                ( 90, self.H-165 + self.height // 2), 
                                ( 100, self.H-165 + self.height // 2 + 10), 
                                4)
            pygame.draw.line(self.surface, WHITE, 
                                ( 100, self.H-165 + self.height // 2 + 10), 
                                ( 115, self.H-165 + self.height // 2 - 10), 
                                4)

            #dessiner le texte
            draw_text(self.text,SMALL_FONT,BLACK,self.surface,50 + self.width // 2, self.H-180 + self.height // 2)
            draw_text(self.description,SMALL_FONT,LIGHT_GRAY,self.surface,50 + self.width // 2, self.H-150 + self.height // 2)