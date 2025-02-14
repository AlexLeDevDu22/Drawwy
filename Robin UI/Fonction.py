import pygame
from PIL import Image, ImageFilter

NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

pygame.font.init()
font = pygame.font.Font(None, 24)


def flou(pygame_surface, blur_radius=3.5):
    width, height = pygame_surface.get_size()
    image_str = pygame.image.tostring(pygame_surface, "RGBA")
    image_pil = Image.frombytes("RGBA", (width, height), image_str)
    blurred_pil = image_pil.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred_str = blurred_pil.tobytes()
    blurred_surface = pygame.image.fromstring(blurred_str, (width, height), "RGBA")
    return blurred_surface

#def banniere(pseudo,points,pdp,couleurs,trouver,numero):