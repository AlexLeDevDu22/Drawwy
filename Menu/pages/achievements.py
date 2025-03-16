from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text
from shared.ui.elements import Button
from shared.utils.data_manager import *

def show_achievements(screen,W,H, mouse_pos, mouse_click, buttons):
    
    # Titre
    draw_text("SUCCÈS", BUTTON_FONT, BLACK, screen, W // 2, 100)
    
    # Panneau principal
    main_panel_width = 800
    main_panel_height = 500
    main_panel_x = (W - main_panel_width) // 2
    main_panel_y = 180
    
    pygame.draw.rect(screen, DARK_BEIGE, 
                    (main_panel_x + 10, main_panel_y + 10, 
                        main_panel_width, main_panel_height), 
                    border_radius=30)
    
    pygame.draw.rect(screen, BEIGE, 
                    (main_panel_x, main_panel_y, 
                        main_panel_width, main_panel_height), 
                    border_radius=30)
    

    achievement_y = main_panel_y + 60
    achievement_height = 70
    
    for achievement in PLAYER_DATA["achievements"]:
        # Fond
        color = PASTEL_GREEN if achievement["succeed"] else LIGHT_GRAY
        pygame.draw.rect(screen, color, 
                        (main_panel_x + 50, achievement_y, 
                            main_panel_width - 100, achievement_height), 
                        border_radius=15)
        
        # Texte
        draw_text(achievement["title"], SMALL_FONT, BLACK, screen, 
                    main_panel_x + 400, achievement_y + 20)
        
        description_font = pygame.font.SysFont(None, 30)
        draw_text(achievement["explication"], description_font, GRAY, screen, 
                    main_panel_x + 400, achievement_y + 50)
        
        # Icône
        if achievement["succeed"]:
            pygame.draw.circle(screen, DARK_BLUE, 
                                (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                20)
            pygame.draw.line(screen, WHITE, 
                            (main_panel_x + 90, achievement_y + achievement_height // 2), 
                            (main_panel_x + 100, achievement_y + achievement_height // 2 + 10), 
                            4)
            pygame.draw.line(screen, WHITE, 
                            (main_panel_x + 100, achievement_y + achievement_height // 2 + 10), 
                            (main_panel_x + 115, achievement_y + achievement_height // 2 - 10), 
                            4)
        else:
            pygame.draw.circle(screen, GRAY, 
                                (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                20)
            pygame.draw.circle(screen, color, 
                                (main_panel_x + 100, achievement_y + achievement_height // 2), 
                                16)
        if achievement["succeed"]:
            color=achievement["couleurs"]
            b_size=3
        else:
            color=(min(255, achievement["couleurs"][0]+50), min(255, achievement["couleurs"][1]+50), min(255, achievement["couleurs"][2]+50))
            b_size=2
        pygame.draw.rect(screen, SOFT_ORANGE if achievement["succeed"] else GRAY, 
                        (main_panel_x + main_panel_width - 115-b_size, achievement_y + (achievement_height-50)//2-b_size, 50+b_size*2, 50+b_size*2), 
                        border_radius=12)
        pygame.draw.rect(screen, color, 
                        (main_panel_x + main_panel_width - 115, achievement_y + (achievement_height-50)//2, 50, 50), 
                        border_radius=12)
        
        achievement_y += achievement_height + 10
    
    # Bouton de retour

    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    if buttons["back"].check_hover(mouse_pos) and mouse_click:
        return screen, "home", buttons
    buttons["back"].draw(screen)
    return screen, "achievements", buttons
    