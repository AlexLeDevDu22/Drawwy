from shared.ui.common_ui import *
from shared.utils.common_utils import draw_text
from shared.ui.elements import Button
import json

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
    
    # Liste de succès fictifs
    with open("data/players_data.json") as f:
        players_data = json.load(f)

    achievements = [
        {"name": "Premier Tracé", "description": "Tracé quelque chose", "completed": players_data["achievements"][0]["succeed"]},
        {"name": "Artiste en herbe", "description": "Dessinez 10 dessins", "completed": players_data["achievements"][1]["succeed"]},
        {"name": "Maître du crayon", "description": "Dessinez 50 dessins", "completed": players_data["achievements"][2]["succeed"]},
        {"name": "Collaborateur", "description": "Jouez en multijoueur 5 fois", "completed": players_data["achievements"][3]["succeed"]},
        {"name": "Perfectionniste", "description": "Obtenez un score parfait", "completed": players_data["achievements"][4]["succeed"]}
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

    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    if buttons["back"].check_hover(mouse_pos) and mouse_click:
        return screen, "home", buttons
    buttons["back"].draw(screen)
    return screen, "achievements", buttons
    