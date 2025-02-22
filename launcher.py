import pygetwindow as gw
import pygame

connected = False

def draw_gradient(screen, color1, color2):
    """Crée un dégradé vertical"""
    width, height = screen.get_size()
    for y in range(height):
        r = color1[0] + (color2[0] - color1[0]) * y // height
        g = color1[1] + (color2[1] - color1[1]) * y // height
        b = color1[2] + (color2[2] - color1[2]) * y // height
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

def launcher():
    global connected

    pygame.init()
    icon = pygame.image.load("icon.png")
    pygame.display.set_icon(icon)
    screen = pygame.display.set_mode((350, 300), pygame.NOFRAME)
    pygame.display.set_caption("Drawwy")
    clock = pygame.time.Clock()

    # Essayons de mettre la fenêtre au premier plan
    try:
        gw.getWindowsWithTitle("Drawwy")[0].activate()
    except:
        pass

    # Charger la police
    police = pygame.font.Font("PermanentMarker.ttf", 20)

    while not connected:
        # Gestion des événements pour éviter le crash
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Dégradé de fond (orange -> jaune clair)
        draw_gradient(screen, (255, 150, 50), (255, 220, 100))

        # Affichage de l'icône
        image = pygame.transform.scale(icon, (200, 200))
        screen.blit(image, (75, 35))

        # Texte de connexion
        text = police.render("Connexion au serveur...", True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=(screen.get_width() // 2 + 5, 235)))

        # Mise à jour de l'affichage
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
