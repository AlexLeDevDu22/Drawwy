import cv2
import numpy as np
import pygame
import random
from skimage.metrics import structural_similarity as ssim


def simplify_image(
        image,
        num_colors=12,
        contrast_threshold=20,
        color_boost=1.3,
        clean_size=3):
    """
    Simplifie une image en réduisant le nombre de couleurs, en augmentant la saturation des couleurs faibles, en détectant les zones à faible contraste et en supprimant les petits points.

    Parameters
    ----------
    image : array
        L'image à simplifier.
    num_colors : int
        Nombre de couleurs à garder. (défaut: 12)
    contrast_threshold : int

        Valeur de seuil pour la détection des contrastes. (défaut: 20)
    color_boost : float
        Facteur d'ajustement de la saturation. (défaut: 1.3)
    clean_size : int
        Taille du noyau pour la suppression des petits points. (défaut: 3)

    Returns
    -------
    array
        L'image simplifiée.
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir BGR en RGB
    pixels = image.reshape((-1, 3)).astype(np.float32)

    # Réduction des couleurs avec k-means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, palette = cv2.kmeans(
        pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    simplified_image = palette[labels.flatten()].reshape(
        image.shape).astype(np.uint8)

    # Détection des contrastes
    gray = cv2.cvtColor(simplified_image, cv2.COLOR_RGB2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    contrast_map = np.abs(laplacian)
    low_contrast_mask = contrast_map < contrast_threshold

    # Ajustement de la saturation
    hsv = cv2.cvtColor(simplified_image, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    s[low_contrast_mask] = np.clip(s[low_contrast_mask] * color_boost, 0, 255)
    hsv = cv2.merge([h, s, v])
    color_boosted_image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    # Suppression des petits points
    kernel = np.ones((clean_size, clean_size), np.uint8)
    image = cv2.morphologyEx(color_boosted_image, cv2.MORPH_OPEN, kernel)

    return image


def extract_important_shapes(image):
    """
    Extrait les contours importants d'une image.

    Utilise une threshold adaptative pour détecter les contours, puis dilate l'image pour
    fermer les petits espaces et élargir les contours.

    Parameters
    ----------
    image : array
        L'image en entrée.

    Returns
    -------
    array
        L'image avec les contours importants.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(adaptive_thresh, kernel, iterations=1)
    return edges


def compare_images(solo_class, img1_path, img2_surface):
    """
    Compare two images and return a score based on the similarity of the shapes.

    Parameters
    ----------
    solo_class : SoloGame
        The SoloGame instance to store the result in.
    img1_path : str
        The path to the first image.
    img2_surface : pygame.Surface
        The second image as a pygame surface.

    Returns
    -------
    int
        A score between 0 and 100 based on the similarity of the shapes.

    Notes
    -----
    The comparison is done in the following steps:
    1. Simplification of the images to reduce the number of colors.
    2. Extraction of the important shapes using an adaptive threshold.
    3. Comparison of the shapes using the SSIM metric.
    4. Calculation of the surface ratio between the two images.
    5. Comparison of the global pixel values to detect major differences.
    6. Comparison of the colors in the important zones.
    7. Final score calculation based on the above steps.
    """
    solo_class.similarity_score = -1

    img1 = cv2.imread(img1_path)
    img1 = simplify_image(img1, num_colors=6)

    img2 = pygame.surfarray.array3d(img2_surface)
    img2 = np.transpose(img2, (1, 0, 2))
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    img2 = simplify_image(img2, num_colors=6)

    # Extraction des formes importantes
    edges1 = extract_important_shapes(img1)
    edges2 = extract_important_shapes(img2)

    # Vérification si le dessin est presque vide
    white_ratio = np.mean(img2) / 255  # % de blanc dans l'image
    if white_ratio > 0.9 or np.mean(edges2) < 5:
        solo_class.similarity_score = random.randint(1, 5)
        solo_class.similarity_score_ready = True
        return 5

    # Comparaison des formes (SSIM)
    ssim_score, _ = ssim(edges1, edges2, full=True)
    shape_score = ssim_score * 100

    # Calcul du taux de remplissage
    nonzero1 = np.count_nonzero(edges1)
    nonzero2 = np.count_nonzero(edges2)

    if nonzero2 == 0:
        solo_class.similarity_score = 0
        solo_class.similarity_score_ready = True
        return 0

    surface_ratio = min(nonzero2 / nonzero1, nonzero1 / nonzero2) * 100
    surface_score = max(0, surface_ratio)

    # Comparaison des pixels globaux pour détecter les différences majeures
    pixel_diff = np.mean(
        np.abs(img1.astype("float") - img2.astype("float"))) / 255
    # Si les pixels sont trop différents, baisse la note
    pixel_penalty = max(0, (1 - pixel_diff) * 100)

    # Comparaison des couleurs dans les zones importantes
    mask = edges1 > 0
    img1_colors = img1[mask]
    img2_colors = img2[mask]

    if len(img1_colors) > 0 and len(img2_colors) > 0:
        diff_color = np.mean(
            np.abs(
                img1_colors.astype("float") -
                img2_colors.astype("float")))
        color_score = max(0, 100 - diff_color * 0.2)
    else:
        color_score = 50

    # Score final équilibré
    final_score = int((shape_score * 0.5) + (surface_score * 0.3) +
                      (color_score * 0.1) - (pixel_penalty * 0.1))

    solo_class.similarity_score = final_score
    solo_class.similarity_score_ready = True

    return final_score
