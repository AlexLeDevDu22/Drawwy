import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def compare_images(img1_path, img2_path):
    # Charger les images
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    # Vérifier si les images ont été chargées
    if img1 is None:
        print(f"Erreur : Impossible de charger {img1_path}")
        return None
    if img2 is None:
        print(f"Erreur : Impossible de charger {img2_path}")
        return None

    # Redimensionner img2 pour qu'elle ait la même taille qu'img1
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Calculer la similarité SSIM
    score, _ = ssim(img1, img2, full=True)
    return score * 100


img1 = "tests/test_histoire/image1.png"
img2 = "tests/test_histoire/image2.png"

similarity = compare_images(img1, img2)

if similarity is not None:
    print(f"Similarité : {similarity:.2f}%")
else:
    print("Comparaison impossible.")
