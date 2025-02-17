import pygetwindow as gw
import pygame

connected=False
def launcher():
    global connected

    pygame.init()
    screen = pygame.display.set_mode((400, 200), pygame.NOFRAME)
    pygame.display.set_caption("Drawwy")
    try:gw.getWindowsWithTitle("Drawwy")[0].activate()  # First plan
    except:pass
    clock = pygame.time.Clock()

    while not connected:
        screen.fill((255, 180, 50))
        
        image = pygame.image.load("launcher.png")
        image = pygame.transform.scale(image, (200, 200))
        screen.blit(image, (100, 0))
        
        police = pygame.font.Font("PermanentMarker.ttf" ,20)
        text = police.render ( "Connexion au serveur...", 1 , (0,0,0) )
        screen.blit(text, text.get_rect(center=(screen.get_width() // 2+5, 170)))
                
        pygame.display.flip()
        clock.tick(10)
        
    pygame.quit()