import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from SoloGame.pages.image_comparaison import popup_result
import os
import pygame

def compare_images(img1_path, img2_surface):

    # Charger l'image classique
    img1 = cv2.imread(img1_path)

    # Convertir la surface Pygame en une image compatible OpenCV
    img2 = pygame.surfarray.array3d(img2_surface)  # Convertir en array NumPy
    img2 = np.transpose(img2, (1, 0, 2))  # Transposer les dimensions pour correspondre à OpenCV

    # Redimensionner img2 pour qu'elle ait la même taille qu'img1
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Convertir en niveaux de gris
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)  # Utilise RGB car c'est l'ordre des couleurs avec Pygame

    # Calculer la similarité SSIM
    score, _ = ssim(img1_gray, img2_gray, full=True)

    return int(score * 100)  # Retourne la similarité en pourcentage
