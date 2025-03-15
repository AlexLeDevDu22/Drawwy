from shared.ui.common_ui import *
from shared.utils.common_utils import *
from shared.ui.elements import Button

def play_choicer(screen, W, H, mouse_pos, mouse_click, connected, buttons):
    # Titre
    draw_text("Mode de jeu", BUTTON_FONT, BLACK, screen, W // 2, 100)
    
    # Options de jeu
    game_modes = ["Solo", "Multijoueur"]
    mode_width = 300
    mode_height = 200
    modes_y = H // 2 - mode_height // 2
    
    total_width = len(game_modes) * mode_width + (len(game_modes) - 1) * 50
    start_x = (W - total_width) // 2
    
    for i, mode in enumerate(game_modes):
        mode_x = start_x + i * (mode_width + 50)
        mode_rect = pygame.Rect(mode_x, modes_y, mode_width, mode_height)
        
        # Vérifier si la souris survole
        hover = mode_rect.collidepoint(mouse_pos) and (mode=="Solo" or connected)
        
        # Dessiner l'ombre
        pygame.draw.rect(screen, DARK_BEIGE, 
                        (mode_x + 10, modes_y + 10, mode_width, mode_height), 
                        border_radius=20)
        
        # Dessiner le fond
        color = SOFT_ORANGE if hover else BEIGE
        pygame.draw.rect(screen, color, mode_rect, border_radius=20)
        
        # Dessiner le texte
        draw_text(mode, SMALL_FONT, BLACK if mode=="Solo" or connected else RED, screen, 
                    mode_x + mode_width // 2, modes_y + mode_height // 2)
        
        # Gérer le clic
        if mouse_click and hover:
            if mode=="Solo" or connected:
                return screen, mode, buttons
    
    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    if buttons["back"].check_hover(mouse_pos) and mouse_click:
        return screen, "home", buttons
    buttons["back"].draw(screen)
    return screen, "play", buttons