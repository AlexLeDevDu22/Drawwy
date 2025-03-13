from shared.common_ui import *
from shared.common_utils import draw_text, draw_textbox


def show_achievements(screen,W,H, mouse_pos, mouse_click):
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
    
    # Liste de succès fictifs
    achievements = [
        {"name": "Premier dessin", "description": "Complétez votre premier dessin", "completed": True},
        {"name": "Artiste en herbe", "description": "Dessinez 10 dessins", "completed": True},
        {"name": "Maître du crayon", "description": "Dessinez 50 dessins", "completed": False},
        {"name": "Collaborateur", "description": "Jouez en multijoueur 5 fois", "completed": False},
        {"name": "Perfectionniste", "description": "Obtenez un score parfait", "completed": False}
    ]
    
    achievement_y = main_panel_y + 60
    achievement_height = 70
    
    for achievement in achievements:
        # Fond
        color = PASTEL_GREEN if achievement["completed"] else LIGHT_GRAY
        pygame.draw.rect(screen, color, 
                        (main_panel_x + 50, achievement_y, 
                            main_panel_width - 100, achievement_height), 
                        border_radius=15)
        
        # Texte
        draw_text(achievement["name"], SMALL_FONT, BLACK, screen, 
                    main_panel_x + 400, achievement_y + 20)
        
        description_font = pygame.font.SysFont(None, 30)
        draw_text(achievement["description"], description_font, GRAY, screen, 
                    main_panel_x + 400, achievement_y + 50)
        
        # Icône
        if achievement["completed"]:
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
        
        achievement_y += achievement_height + 10
    
    # Bouton de retour
    back_button_rect = draw_textbox("RETOUR", W // 2 - 100, H - 100, 
                                    200, 50, SMALL_FONT, BLACK, ORANGE, screen, 25)
    
    if mouse_click and back_button_rect.collidepoint(mouse_pos):
        return screen, "menu"
    return screen, "achievements"
    