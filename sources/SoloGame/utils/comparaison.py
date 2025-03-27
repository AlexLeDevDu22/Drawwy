import cv2
import numpy as np
import pygame
from skimage.metrics import structural_similarity as ssim
from sympy import im

def compare_images(solo_class, img1_path, img2_surface):
    """
    Compare two images (an image path and a Pygame surface) to calculate a similarity score.
    The score is based on the following criteria:
    1. Contours: Verifies that the overall shape is respected using the Canny edge detector.
    2. Drawing ratio: Verifies that the quantity of drawing is similar to the model.
    3. Color comparison: Compares the color histogram of the drawing, ignoring the white background.
    4. Global structure comparison: Compares the global structure of the drawing using the Structural Similarity Index (SSIM).
    The final score is a weighted sum of these criteria, with the following weights:
    - Similarity: 50%
    - Contours: 40%
    - Drawing ratio: 20%
    - Color comparison: 10%
    The score is expressed as a percentage and is stored in the solo_class instance.

    :param solo_class: The SoloGame instance to store the similarity score in.
    :param img1_path: The path to the reference image.
    :param img2_surface: The Pygame surface to compare with the reference image.
    :return: The similarity score as a percentage.
    """
    solo_class.similarity_score = -1

    # Charger l'image de référence et la convertir en niveaux de gris
    ref_img = cv2.imread(img1_path)
    ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)

    # Convertir la surface pygame en image OpenCV
    img2_surface_bytes = pygame.image.tostring(img2_surface, "RGB")
    player_img = np.frombuffer(img2_surface_bytes, dtype=np.uint8).reshape((img2_surface.get_height(), img2_surface.get_width(), 3))
    player_gray = cv2.cvtColor(player_img, cv2.COLOR_RGB2GRAY)

    # Redimensionner à la même taille
    player_gray = cv2.resize(player_gray, (ref_gray.shape[1], ref_gray.shape[0]))
    player_img = cv2.resize(player_img, (ref_img.shape[1], ref_img.shape[0]))

    # --- 1. Contours : Vérifier si la forme générale est respectée ---
    ref_edges = cv2.Canny(ref_gray, 50, 150)
    player_edges = cv2.Canny(player_gray, 50, 150)
    edge_similarity, _ = ssim(ref_edges, player_edges, full=True)

    # --- 2. Vérifier la quantité de dessin par rapport au modèle ---
    ref_non_white = np.count_nonzero(ref_gray < 250)
    player_non_white = np.count_nonzero(player_gray < 250)
    drawing_ratio = min(1, player_non_white / max(1, ref_non_white))  # Évite division par 0

    # --- 3. Comparaison de couleur mais en ignorant le fond blanc ---
    mask_ref = (ref_gray < 250)  # Pixels dessinés dans le modèle
    mask_player = (player_gray < 250)  # Pixels dessinés par le joueur

    if np.count_nonzero(mask_ref) > 0 and np.count_nonzero(mask_player) > 0:
        # On garde uniquement les pixels non blancs pour l'histogramme
        ref_pixels = ref_img[mask_ref]
        player_pixels = player_img[mask_player]

        # Vérifier si les matrices ne sont pas vides
        if ref_pixels.shape[0] > 0 and player_pixels.shape[0] > 0:
            ref_color_hist = cv2.calcHist([ref_pixels], [0], None, [8], [0, 256])
            player_color_hist = cv2.calcHist([player_pixels], [0], None, [8], [0, 256])
            color_similarity = cv2.compareHist(ref_color_hist, player_color_hist, cv2.HISTCMP_CORREL)
        else:
            color_similarity = 0  # Si les images sont vides après filtrage
    else:
        color_similarity = 0  # Si rien n'est dessiné

    # --- 4. Comparaison globale de la structure du dessin ---
    similarity, _ = ssim(ref_gray, player_gray, full=True)

    # --- 5. Score final avec meilleures pondérations ---
    score = (similarity * 0.5 + edge_similarity * 0.4 + drawing_ratio * 0.2 + color_similarity * 0.1) * 100

    # Appliquer des pénalités sévères si contours ou dessin absent
    if drawing_ratio < 0.3:  # Si moins de 30% du modèle est dessiné
        score *= 0.5
    if edge_similarity < 0.2:  # Si les formes sont trop différentes
        score *= 0.5

    # Normaliser entre 0 et 100
    score = max(0, min(100, int(score)))

    solo_class.similarity_score = score
    solo_class.similarity_score_ready = True

    return score