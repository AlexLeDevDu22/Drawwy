from shared.ui.common_ui import *
from shared.utils.common_utils import *
from shared.ui.elements import Button
import requests

# Adresses des serveurs (exemple)
SERVERS = {
    "Inferno Arena": "http://server1.com/player_count",
    "Frostbyte Nexus": "http://server2.com/player_count",
    "Nebula Realm": "http://server3.com/player_count"
}

def get_player_count(server_url):
    """Récupère le nombre de joueurs connectés sur un serveur."""
    try:
        response = requests.get(server_url, timeout=2)
        if response.status_code == 200:
            return response.json().get("player_count", "?")
    except:
        return "?"

def play_choicer(screen, W, H, mouse_pos, mouse_click, connected, buttons):
    # Titre
    draw_text("Choisissez votre serveur", BUTTON_FONT, BLACK, screen, W // 2, 100)

    # Serveurs disponibles
    server_width = 300
    server_height = 200
    servers_y = H // 2 - server_height // 2
    
    total_width = len(CONFIG["servers"]) * server_width + (len(CONFIG["servers"]) - 1) * 50
    start_x = (W - total_width) // 2
    
    for i, (server_name, server) in enumerate(CONFIG["servers"].items()):


        server_x = start_x + i * (server_width + 50)
        server_rect = pygame.Rect(server_x, servers_y, server_width, server_height)
        
        # Vérifier si la souris survole
        hover = server_rect.collidepoint(mouse_pos) and connected
        
        # Récupérer le nombre de joueurs
        player_count = get_player_count("https://"+server["domain"])
        
        # Dessiner l'ombre
        pygame.draw.rect(screen, DARK_BEIGE, 
                        (server_x + 10, servers_y + 10, server_width, server_height), 
                        border_radius=20)
        
        # Dessiner le fond
        color = SOFT_ORANGE if hover else BEIGE
        pygame.draw.rect(screen, color, server_rect, border_radius=20)
        
        # Dessiner le nom du serveur
        draw_text(server_name, SMALL_FONT, BLACK, screen, 
                    server_x + server_width // 2, servers_y + 50)

        # Afficher le nombre de joueurs
        draw_text(f"👥 {player_count} joueurs", SMALL_FONT, DARK_GRAY, screen, 
                    server_x + server_width // 2, servers_y + 130)
        
        # Gérer le clic
        if mouse_click and hover:
            return screen, server_name, buttons

    # Bouton retour
    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    if buttons["back"].check_hover(mouse_pos) and mouse_click:
        return screen, "home", buttons
    buttons["back"].draw(screen)

    return screen, "play", buttons
