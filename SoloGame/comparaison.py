import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def compare_images(img1_path, img2_path):
    # Charger les images
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    # Vérifier si les images existent
    if img1 is None:
        print(f"Erreur : Impossible de charger {img1_path}")
        return None
    if img2 is None:
        print(f"Erreur : Impossible de charger {img2_path}")
        return None

    # Redimensionner img2 pour qu'elle ait la même taille qu'img1
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Convertir en niveaux de gris
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Calculer la similarité SSIM
    score, _ = ssim(img1_gray, img2_gray, full=True)

    return score * 100  # Retourne la similarité en pourcentage
