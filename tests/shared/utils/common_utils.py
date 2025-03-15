from shared.ui.common_ui import *

import pygame

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def achievement_popup(text,description,H,W,surface,font):
    #dessiner la boite
    width = 500
    height = 100
    box_rect_achievement = pygame.Rect(50,H-165,width,height)
    pygame.draw.rect(surface,PASTEL_GREEN,box_rect_achievement,border_radius=15)
    #rond valide
    pygame.draw.circle(surface, DARK_BLUE, 
                            ( 100, H-165+ height // 2), 
                            20)
    pygame.draw.line(surface, WHITE, 
                        ( 90, H-165 + height // 2), 
                        ( 100, H-165 + height // 2 + 10), 
                        4)
    pygame.draw.line(surface, WHITE, 
                        ( 100, H-165 + height // 2 + 10), 
                        ( 115, H-165 + height // 2 - 10), 
                        4)

    #dessiner le texte
    draw_text(text,font,BLACK,surface,50 + width // 2, H-180 + height // 2)
    draw_text(description,font,LIGHT_GRAY,surface,50 + width // 2, H-150 + height // 2)

    
