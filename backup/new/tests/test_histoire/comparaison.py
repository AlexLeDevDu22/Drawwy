import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def reduce_colors(image, k=16):
    """ Réduit le nombre de couleurs de l'image à k couleurs. """
    Z = image.reshape((-1, 3))
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(
        Z, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    result = centers[labels.flatten()].reshape(image.shape)
    return result


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

    # Réduction des couleurs à 16
    img1 = reduce_colors(img1, k=16)
    img2 = reduce_colors(img2, k=16)

    # Conversion en niveaux de gris
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Calculer la similarité SSIM
    score, _ = ssim(img1_gray, img2_gray, full=True)
    return score * 100


# 🔥 Exemple d'utilisation (METTRE LES CHEMINS ABSOLUS)
img1 = "tests/test_histoire/image1.png"
img2 = "tests/test_histoire/image2.png"

similarity = compare_images(img1, img2)

if similarity is not None:
    print(f"Similarité : {similarity:.2f}%")
else:
    print("Comparaison impossible.")
