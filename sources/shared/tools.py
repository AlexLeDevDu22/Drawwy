import socket
import pygame
import random
import time

from shared.ui.elements import Particle
from shared.ui.common_ui import *


def is_connected():
    """
    Vérifie si l'ordinateur est connect  internet.

    Cette fonction tente de se connecter au serveur DNS public de Google
    (8.8.8.8) sur le port 53 et renvoie True si la connexion est établie
    et False sinon.
    """
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def get_screen_size():
    info_ecran = pygame.display.Info()
    return info_ecran.current_w, info_ecran.current_h


def show_emote(screen, emote, x, y, size):
    """
    Affiche un emote (image ou GIF) sur une surface Pygame.

    L'emote est dessinée à la position (x, y) sur la surface `screen` en la
    redimensionnant au format `(size, size)`.

    Si l'emote est un GIF, la fonction calcule automatiquement la frame
    actuelle en fonction de l'horodatage de démarrage du GIF (`emote["gif_start_time"]`)
    et de la durée d'une frame (`emote["gif_frame_duration"]`).

    :param screen: Surface Pygame sur laquelle afficher l'emote.
    :param emote: Dictionnaire contenant les informations de l'emote.
    :param x: Coordonnée x de l'emote.
    :param y: Coordonnée y de l'emote.
    :param size: Taille de l'emote.
    :type screen: pygame.Surface
    :type emote: dict
    :type x: int
    :type y: int
    :type size: int
    """
    if emote["type"] == "image":
        emote_img = pygame.transform.scale(emote["image_pygame"], (size, size))
    else:  # GIF
        current_frame_index = int(
            (time.time() - emote["gif_start_time"]) * emote["gif_frame_duration"]) % len(
            emote["gif_frames"])
        emote_img = pygame.transform.scale(
            emote["gif_frames"][current_frame_index], (size, size))
    screen.blit(emote_img, (x, y))


def apply_circular_mask(image):
    # Créer un masque avec canal alpha
    """
    Applique un masque circulaire avec transparence à une image Pygame.

    La fonction crée un masque circulaire avec un canal alpha, le dessine sur
    une surface Pygame, puis applique ce masque sur l'image en utilisant la
    fonction `blit` avec le drapeau `BLEND_RGBA_MULT`. Cela permet de donner
    une forme circulaire à l'image tout en laissant les pixels transparents.
    """
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


def generate_particles(
    n,
    x1,
    y1,
    x2,
    y2,
    colors=[
        SOFT_ORANGE,
        PASTEL_PINK,
        PASTEL_GREEN,
        PASTEL_YELLOW]):
    """
    Generate a list of particles with random positions and colors.

    This function creates a specified number of particles, each with a random
    position within a defined rectangular area and a random color from a given
    list. The particles are instances of the `Particle` class.

    :param n: Number of particles to generate.
    :type n: int
    :param x1: Minimum x-coordinate for particle position.
    :type x1: int
    :param y1: Minimum y-coordinate for particle position.
    :type y1: int
    :param x2: Maximum x-coordinate for particle position.
    :type x2: int
    :param y2: Maximum y-coordinate for particle position.
    :type y2: int
    :param colors: List of possible colors for the particles.
    :type colors: list of tuples
    :return: List of generated Particle objects.
    :rtype: list of Particle
    """

    particles = []
    for _ in range(n):
        particles.append(Particle(
            random.randint(x1, x2),
            random.randint(y1, y2),
            random.choice(colors)
        ))

    return particles
