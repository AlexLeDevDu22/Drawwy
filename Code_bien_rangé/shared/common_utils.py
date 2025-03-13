import pygame

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