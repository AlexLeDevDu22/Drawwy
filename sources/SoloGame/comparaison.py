import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from SoloGame.pages.image_comparaison import popup_result
import os

def compare_images(img1_path, img2_path):
    # Afficher les chemins pour debug
    print(f"Chemin image 1 : {img1_path}")
    print(f"Chemin image 2 : {img2_path}")

    # Vérifier si les fichiers existent
    if not os.path.exists(img1_path):
        print(f"Erreur : {img1_path} n'existe pas.")
        return None
    if not os.path.exists(img2_path):
        print(f"Erreur : {img2_path} n'existe pas.")
        return None

    # Charger les images
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    # Vérifier si les images sont bien chargées
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

    return int(score * 100)  # Retourne la similarité en pourcentage
