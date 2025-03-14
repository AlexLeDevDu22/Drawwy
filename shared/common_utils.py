import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (170, 170, 170)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (65, 105, 225)
LIGHT_BLUE = (119, 181, 254)
VERY_LIGHT_BLUE= (160, 205, 255)
ORANGE = (255, 95, 31)
SOFT_ORANGE = (255, 160, 122)
BEIGE = (245, 222, 179)
DARK_BEIGE = (222, 184, 135)
PASTEL_PINK = (255, 209, 220)
PASTEL_GREEN = (193, 225, 193)
PASTEL_YELLOW = (253, 253, 150)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
LIGHT_BEIGE = (239, 231, 219)
LIGHT_ORANGE = (255, 219, 187)

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def draw_textbox(text, x, y, width, height, font, text_color, bg_color, surface, border_radius=10):
    # Dessiner la boîte
    box_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, bg_color, box_rect, border_radius=border_radius)
    
    # Dessiner le texte
    draw_text(text, font, text_color, surface, x + width // 2, y + height // 2)
    
    return box_rect
def draw_texte_achievement(text,description,H,W,surface,font):
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

    
