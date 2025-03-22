import cv2
import numpy as np
import pygame
from skimage.metrics import structural_similarity as ssim


def compare_images(model_path, pygame_img):
    # Charger l'image modèle depuis le chemin
    img1 = cv2.imread(model_path)

    # Convertir la surface pygame en un tableau numpy compatible avec OpenCV
    img2 = pygame.surfarray.array3d(pygame_img)  # Convertit la surface en array (R, G, B)
    img2 = np.transpose(img2, (1, 0, 2))  # Réorganise les axes (pygame et OpenCV n'ont pas le même format)
    img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2BGR)  # Convertit RGB → BGR pour correspondre à OpenCV

    # Redimensionner img2 pour qu'elle ait la même taille qu'img1
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Convertir en niveaux de gris
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Calculer la similarité SSIM
    score, _ = ssim(img1_gray, img2_gray, full=True)

    return score * 100  # Retourne la similarité en pourcentage