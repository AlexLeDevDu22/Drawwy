import cv2
import numpy as np
import pygame
from skimage.metrics import structural_similarity as ssim

def simplify_image(image, num_colors=12, contrast_threshold=20, color_boost=1.3, clean_size=3):
    """Simplifie une image en réduisant le nombre de couleurs et en supprimant les petits détails."""
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir BGR en RGB
    pixels = image.reshape((-1, 3)).astype(np.float32)
    
    # Réduction des couleurs avec k-means
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, palette = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    simplified_image = palette[labels.flatten()].reshape(image.shape).astype(np.uint8)
    
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
    final_image = cv2.morphologyEx(color_boosted_image, cv2.MORPH_OPEN, kernel)
    
    return final_image

def extract_important_shapes(image):
    """ Détecte les zones importantes avec une meilleure précision. """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Filtre adaptatif pour éliminer le bruit tout en gardant les contrastes
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Fermer les formes (évite les contours trop fragmentés)
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(adaptive_thresh, kernel, iterations=1)

    return edges

def compare_images(img1_path, img2_surface):
    """Compare une image de référence et un dessin fait par l'utilisateur."""
    img1 = cv2.imread(img1_path)
    img1 = simplify_image(img1, num_colors=12)
    
    img2 = pygame.surfarray.array3d(img2_surface)
    img2 = np.transpose(img2, (1, 0, 2))
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    img2 = simplify_image(img2, num_colors=12)
    
    # Extraction des formes importantes
    edges1 = extract_important_shapes(img1)
    edges2 = extract_important_shapes(img2)
    
    # Vérifier si l'image dessinée est vide
    if np.mean(edges2) < 5:
        return 0  # Rien n'a été dessiné
    
    # Comparaison de la similarité des formes (SSIM)
    ssim_score, _ = ssim(edges1, edges2, full=True)
    shape_score = ssim_score * 100
    
    # Densité des bords dans l'image de référence et l'image dessinée
    edge_density_1 = np.count_nonzero(edges1) / edges1.size
    edge_density_2 = np.count_nonzero(edges2) / edges2.size
    
    # Bonus pour les détails : si l'utilisateur a dessiné des petites formes similaires
    detail_bonus = 0
    if edge_density_2 > edge_density_1 * 1.1:  # Si la densité des bords dans l'image dessinée est plus élevée que le modèle
        detail_bonus = 10  # Ajouter un bonus pour les petits détails

    # Calcul du score de surface
    nonzero1 = np.count_nonzero(edges1)
    nonzero2 = np.count_nonzero(edges2)
    
    if nonzero2 == 0:
        return 0
    
    surface_ratio = min(nonzero2 / nonzero1, nonzero1 / nonzero2) * 100
    surface_score = max(0, surface_ratio)
    
    # Comparaison des couleurs dans les zones importantes
    mask = edges1 > 0
    img1_colors = img1[mask]
    img2_colors = img2[mask]
    
    if len(img1_colors) > 0 and len(img2_colors) > 0:
        diff_color = np.mean(np.abs(img1_colors.astype("float") - img2_colors.astype("float")))
        color_score = max(0, 100 - diff_color * 0.1)
    else:
        color_score = 50
    
    # Calcul du score final avec bonus pour les détails
    final_score = (shape_score * 0.6) + (surface_score * 0.3) + (color_score * 0.1) + detail_bonus
    return int(final_score)