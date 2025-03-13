import socket
import pygame

def is_connected():
    try:
        # Tente de se connecter à un serveur DNS public (Google)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
                
def get_screen_size():
    info_ecran = pygame.display.Info()
    return info_ecran.current_w, info_ecran.current_h

def apply_circular_mask(image):
    """Applique un masque circulaire avec transparence à une image Pygame."""
    # Créer un masque avec canal alpha
    mask = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))  # Transparence totale

    # Dessiner un cercle blanc opaque dans le masque
    pygame.draw.circle(
        mask,
        (255, 255, 255, 255),  # Blanc opaque
        (image.get_width() // 2, image.get_height() // 2),
        image.get_width() // 2,
    )

    # Appliquer le masque sur l'image
    image.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
