from shared.ui.common_ui import *
from shared.utils.common_utils import *
from shared.ui.elements import Button
import requests
import threading

players_per_server = {serv: None for serv in CONFIG["servers"].keys()}

last_check_players=time.time()


def set_player_count(name, server_url):
    """Récupère le nombre de joueurs connectés sur un serveur."""
    global players_per_server
    try:
        response = requests.get(server_url + "/num_players", timeout=4)
        if response.status_code == 200:
            players_per_server[name] = int(
                response.json().get("num_players", 0))
            return
    except BaseException:
        pass
    players_per_server[name] = 0


def choice_server(screen, W, H, mouse_pos, mouse_click, connected, buttons):
    global players_per_server
    # Titre
    draw_text(
        "Choisissez votre serveur",
        BUTTON_FONT,
        BLACK,
        screen,
        W // 2,
        100)

    # Serveurs disponibles
    server_width = 300
    server_height = 200
    servers_y = H // 2 - server_height // 2

    total_width = len(CONFIG["servers"]) * server_width + \
        (len(CONFIG["servers"]) - 1) * 50
    start_x = (W - total_width) // 2

    for i, (server_name, server) in enumerate(CONFIG["servers"].items()):

        server_x = start_x + i * (server_width + 50)
        server_rect = pygame.Rect(
            server_x,
            servers_y,
            server_width,
            server_height)

        # Vérifier si la souris survole
        hover = server_rect.collidepoint(mouse_pos) and connected

        # Récupérer le nombre de joueurs
        if players_per_server[server_name] is None or time.time()-last_check_players>5:
            if players_per_server[server_name] is None:
                players_per_server[server_name] = -1
            threading.Thread(
                target=set_player_count,
                args=(
                    server_name,
                    "https://" +
                    server["domain"],
                )).start()

        # Dessiner l'ombre
        pygame.draw.rect(
            screen,
            DARK_BEIGE,
            (server_x + 10,
             servers_y + 10,
             server_width,
             server_height),
            border_radius=20)

        # Dessiner le fond
        color = SOFT_ORANGE if hover else BEIGE
        pygame.draw.rect(screen, color, server_rect, border_radius=20)

        # Dessiner le nom du serveur
        draw_text(server_name, SMALL_FONT, BLACK, screen,
                  server_x + server_width // 2, servers_y + 50)

        # Afficher le nombre de joueurs
        if isinstance(
                players_per_server[server_name],
                int) and players_per_server[server_name] < 8:
            color = GREEN
        else:
            color = RED

        draw_text(
            f"{
                players_per_server[server_name]} joueurs" if players_per_server[server_name] > 0 else "",
            SMALL_FONT,
            color,
            screen,
            server_x +
            server_width //
            2,
            servers_y +
            130)

        # Gérer le clic
        if mouse_click and hover:
            return screen, "Multi", buttons, server_name

    # Bouton retour
    if "back" not in buttons:
        buttons["back"] = Button("center", H * 0.8, text="RETOUR")
    if buttons["back"].check_hover(mouse_pos) and mouse_click:
        return screen, "home", buttons, None
    buttons["back"].draw(screen)

    return screen, "Select server", buttons, None
