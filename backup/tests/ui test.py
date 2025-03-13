import pygame
import time

pygame.init()

# Création de la fenêtre
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Cinématique Pygame')

# Chargement des images avec vérification
def load_image(path):
    try:
        image = pygame.image.load(path)
        return image
    except pygame.error:
        print(f"Erreur de chargement de l'image : {path}")
        return None

background = load_image('tests/background.png')
character = load_image('tests/character.png')

# Si l'un des assets échoue à charger, quitter
if background is None or character is None:
    pygame.quit()
    exit()

# Redimensionnement des images pour s'adapter à la fenêtre
background = pygame.transform.scale(background, (screen_width, screen_height))
character = pygame.transform.scale(character, (int(screen_width * 0.2), int(screen_height * 0.2)))  # Redimensionner le personnage

# Chargement et démarrage de la musique
try:
    pygame.mixer.music.load('tests/cinematic_music.mp3')
    pygame.mixer.music.play(-1)  # -1 pour répéter en boucle
except pygame.error:
    print("Erreur de chargement de la musique.")
    pygame.quit()
    exit()

# Fonction de cinématique avec un bouton de sortie
def cinematic():
    running = True
    screen.fill((0, 0, 0))  # Fond noir
    screen.blit(background, (0, 0))  # Affichage du fond
    screen.blit(character, (300, 250))  # Affichage du personnage
    pygame.display.update()  # Mise à jour de l'écran
    
    time.sleep(2)  # Pause de 2 secondes
    
    # Affichage du texte
    font = pygame.font.Font(None, 36)
    text = font.render('Voici une cinématique...', True, (255, 255, 255))
    screen.blit(text, (250, 500))
    pygame.display.update()
    
    time.sleep(3)  # Affichage du texte pendant 3 secondes

    # Affichage du bouton pour quitter
    quit_text = font.render('Appuyez sur Q pour quitter', True, (255, 255, 255))
    screen.blit(quit_text, (250, 550))
    pygame.display.update()

    # Attente d'une touche pour quitter
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Quitter si "Q" est pressé
                    running = False
        pygame.time.delay(50)  # Réduire la charge CPU

# Lancer la cinématique
cinematic()

# Fermer proprement
pygame.quit()
