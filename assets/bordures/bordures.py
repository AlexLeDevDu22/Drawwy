import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import numpy as np

# Créer un dossier pour les bordures si nécessaire
output_dir = 'bordures_profil'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Taille des images
size = 500
img_size = (size, size)
center = (size // 2, size // 2)
border_width = 20

# Fonction pour créer un dégradé radial


def radial_gradient(colors, radius=size // 2):
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for i in range(radius, 0, -1):
        # Interpoler la couleur en fonction de la distance depuis le centre
        idx = (radius - i) / radius
        idx_color = int(idx * (len(colors) - 1))
        color1 = colors[min(idx_color, len(colors) - 1)]
        color2 = colors[min(idx_color + 1, len(colors) - 1)]

        t = idx * (len(colors) - 1) - idx_color
        r = int(color1[0] * (1 - t) + color2[0] * t)
        g = int(color1[1] * (1 - t) + color2[1] * t)
        b = int(color1[2] * (1 - t) + color2[2] * t)

        draw.ellipse(
            (center[0] - i,
             center[1] - i,
                center[0] + i,
                center[1] + i),
            fill=(
                r,
                g,
                b,
                255),
            outline=None)

    return img

# 1. Bronze


def create_bronze_border():
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    bronze_colors = [(205, 127, 50), (230, 177, 127), (140, 83, 33)]

    # Cercle extérieur
    for i in range(border_width):
        draw.ellipse(
            (i,
             i,
             size - i - 1,
             size - i - 1),
            outline=(
                bronze_colors[1][0],
                bronze_colors[1][1],
                bronze_colors[1][2],
                255))

    # Ajouter des détails
    for angle in range(0, 360, 90):
        x = center[0] + int(math.cos(math.radians(angle))
                            * (size // 2 - border_width // 2))
        y = center[1] + int(math.sin(math.radians(angle))
                            * (size // 2 - border_width // 2))
        draw.ellipse(
            (x - 10,
             y - 10,
             x + 10,
             y + 10),
            fill=(
                bronze_colors[0][0],
                bronze_colors[0][1],
                bronze_colors[0][2],
                255))

    # Découpez le centre pour avoir juste la bordure
    mask = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        (border_width * 2,
         border_width * 2,
         size - border_width * 2 - 1,
         size - border_width * 2 - 1),
        fill=255)
    cut_center = Image.new('RGBA', img_size, (0, 0, 0, 0))
    cut_center.paste((0, 0, 0, 0), mask=mask)
    img = Image.composite(cut_center, img, mask)

    img.save(os.path.join(output_dir, 'bronze_border.png'))
    return img

# 2. Silver


def create_silver_border():
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    silver_colors = [(192, 192, 192), (232, 232, 232), (169, 169, 169)]

    # Cercle extérieur avec dégradé
    for i in range(border_width):
        color_idx = i / border_width
        r = int(silver_colors[0][0] * (1 - color_idx) +
                silver_colors[1][0] * color_idx)
        g = int(silver_colors[0][1] * (1 - color_idx) +
                silver_colors[1][1] * color_idx)
        b = int(silver_colors[0][2] * (1 - color_idx) +
                silver_colors[1][2] * color_idx)
        draw.ellipse((i, i, size - i - 1, size - i - 1),
                     outline=(r, g, b, 255))

    # Ajouter des détails en forme de losange
    for angle in range(0, 360, 45):
        x = center[0] + int(math.cos(math.radians(angle))
                            * (size // 2 - border_width // 2))
        y = center[1] + int(math.sin(math.radians(angle))
                            * (size // 2 - border_width // 2))
        draw.ellipse(
            (x - 5,
             y - 5,
             x + 5,
             y + 5),
            fill=(
                silver_colors[1][0],
                silver_colors[1][1],
                silver_colors[1][2],
                255))

    # Découpez le centre
    mask = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        (border_width * 2,
         border_width * 2,
         size - border_width * 2 - 1,
         size - border_width * 2 - 1),
        fill=255)
    cut_center = Image.new('RGBA', img_size, (0, 0, 0, 0))
    cut_center.paste((0, 0, 0, 0), mask=mask)
    img = Image.composite(cut_center, img, mask)

    img.save(os.path.join(output_dir, 'silver_border.png'))
    return img

# 3. Gold


def create_gold_border():
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    gold_colors = [(255, 215, 0), (255, 237, 151), (255, 192, 0)]

    # Créer un dégradé radial
    gradient = radial_gradient(gold_colors)

    # Dessiner le cercle extérieur
    mask_outer = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask_outer)
    mask_draw.ellipse((0, 0, size - 1, size - 1), fill=255)

    mask_inner = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask_inner)
    mask_draw.ellipse(
        (border_width,
         border_width,
         size - border_width - 1,
         size - border_width - 1),
        fill=255)

    # Combiner les masques pour créer la bordure
    mask = ImageChops.difference(mask_outer, mask_inner)
    img.paste(gradient, (0, 0), mask)

    # Ajouter des détails
    for angle in range(0, 360, 30):
        x = center[0] + int(math.cos(math.radians(angle))
                            * (size // 2 - border_width // 2))
        y = center[1] + int(math.sin(math.radians(angle))
                            * (size // 2 - border_width // 2))
        draw.rectangle(
            (x - 6,
             y - 6,
             x + 6,
             y + 6),
            fill=(
                255,
                215,
                0,
                200),
            outline=(
                255,
                255,
                255,
                150))

    img.save(os.path.join(output_dir, 'gold_border.png'))
    return img

# 4. Platinum


def create_platinum_border():
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    platinum_colors = [(229, 228, 226), (247, 247, 247), (201, 201, 201)]

    # Dessiner le cercle principal
    for i in range(border_width):
        color_idx = i / border_width
        r = int(platinum_colors[0][0] * (1 - color_idx) +
                platinum_colors[1][0] * color_idx)
        g = int(platinum_colors[0][1] * (1 - color_idx) +
                platinum_colors[1][1] * color_idx)
        b = int(platinum_colors[0][2] * (1 - color_idx) +
                platinum_colors[1][2] * color_idx)
        draw.ellipse((i, i, size - i - 1, size - i - 1),
                     outline=(r, g, b, 255))

    # Ajouter des détails métalliques
    for i in range(8):
        angle = i * 45
        x1 = center[0] + int(math.cos(math.radians(angle))
                             * (size // 2 - border_width * 1.5))
        y1 = center[1] + int(math.sin(math.radians(angle))
                             * (size // 2 - border_width * 1.5))
        x2 = center[0] + int(math.cos(math.radians(angle))
                             * (size // 2 - border_width / 2))
        y2 = center[1] + int(math.sin(math.radians(angle))
                             * (size // 2 - border_width / 2))
        draw.line((x1, y1, x2, y2), fill=(247, 247, 247, 220), width=3)

    # Effet de lueur
    img = img.filter(ImageFilter.GaussianBlur(1))

    # Découpage du centre
    mask = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        (border_width * 2,
         border_width * 2,
         size - border_width * 2 - 1,
         size - border_width * 2 - 1),
        fill=255)
    cut_center = Image.new('RGBA', img_size, (0, 0, 0, 0))
    cut_center.paste((0, 0, 0, 0), mask=mask)
    img = Image.composite(cut_center, img, mask)

    img.save(os.path.join(output_dir, 'platinum_border.png'))
    return img

# 5. Diamond


def create_diamond_border():
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    diamond_colors = [(185, 242, 255), (137, 207, 240), (100, 149, 237)]

    # Dessiner le cercle de base
    for i in range(border_width):
        color_idx = i / border_width
        r = int(diamond_colors[0][0] * (1 - color_idx) +
                diamond_colors[1][0] * color_idx)
        g = int(diamond_colors[0][1] * (1 - color_idx) +
                diamond_colors[1][1] * color_idx)
        b = int(diamond_colors[0][2] * (1 - color_idx) +
                diamond_colors[1][2] * color_idx)
        draw.ellipse((i, i, size - i - 1, size - i - 1),
                     outline=(r, g, b, 255))

    # Ajouter des "facettes" de diamant
    for i in range(12):
        angle = i * 30
        length = size // 6
        x1 = center[0] + int(math.cos(math.radians(angle))
                             * (size // 2 - border_width - 10))
        y1 = center[1] + int(math.sin(math.radians(angle))
                             * (size // 2 - border_width - 10))
        x2 = center[0] + int(math.cos(math.radians(angle + 15))
                             * (size // 2 - border_width // 2))
        y2 = center[1] + int(math.sin(math.radians(angle + 15))
                             * (size // 2 - border_width // 2))
        draw.line((x1, y1, x2, y2), fill=(185, 242, 255, 200), width=2)

    # Effet de brillance
    img = img.filter(ImageFilter.GaussianBlur(1.5))

    # Ajouter des points brillants
    for i in range(8):
        angle = i * 45
        x = center[0] + int(math.cos(math.radians(angle))
                            * (size // 2 - border_width // 2))
        y = center[1] + int(math.sin(math.radians(angle))
                            * (size // 2 - border_width // 2))
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 255, 255, 230))

    # Découpage du centre
    mask = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        (border_width * 2,
         border_width * 2,
         size - border_width * 2 - 1,
         size - border_width * 2 - 1),
        fill=255)
    cut_center = Image.new('RGBA', img_size, (0, 0, 0, 0))
    cut_center.paste((0, 0, 0, 0), mask=mask)
    img = Image.composite(cut_center, img, mask)

    img.save(os.path.join(output_dir, 'diamond_border.png'))
    return img

# 6. Master


def create_master_border():
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Couleurs dégradées
    master_colors = [(255, 92, 141), (255, 69, 0),
                     (160, 32, 240), (30, 144, 255), (0, 255, 255)]

    # Dessiner le cercle principal
    steps = border_width * 2
    for i in range(steps):
        progress = i / steps
        color_idx = progress * (len(master_colors) - 1)
        idx = int(color_idx)
        t = color_idx - idx

        r = int(master_colors[idx][0] * (1 - t) +
                master_colors[min(idx + 1, len(master_colors) - 1)][0] * t)
        g = int(master_colors[idx][1] * (1 - t) +
                master_colors[min(idx + 1, len(master_colors) - 1)][1] * t)
        b = int(master_colors[idx][2] * (1 - t) +
                master_colors[min(idx + 1, len(master_colors) - 1)][2] * t)

        width = i * border_width // steps
        draw.ellipse(
            (width,
             width,
             size - width - 1,
             size - width - 1),
            outline=(
                r,
                g,
                b,
                255))

    # Dessiner un motif secondaire
    for angle in range(0, 360, 45):
        x1 = center[0] + int(math.cos(math.radians(angle))
                             * (size // 2 - border_width * 2))
        y1 = center[1] + int(math.sin(math.radians(angle))
                             * (size // 2 - border_width * 2))
        x2 = center[0] + int(math.cos(math.radians(angle)) * (size // 2))
        y2 = center[1] + int(math.sin(math.radians(angle)) * (size // 2))

        # Créer un dégradé le long de la ligne
        steps = 20
        for i in range(steps):
            t = i / steps
            x = int(x1 * (1 - t) + x2 * t)
            y = int(y1 * (1 - t) + y2 * t)

            color_idx = t * (len(master_colors) - 1)
            idx = int(color_idx)
            blend = color_idx - idx

            r = int(master_colors[idx][0] *
                    (1 -
                     blend) +
                    master_colors[min(idx +
                                  1, len(master_colors) -
                                      1)][0] *
                    blend)
            g = int(master_colors[idx][1] *
                    (1 -
                     blend) +
                    master_colors[min(idx +
                                  1, len(master_colors) -
                                      1)][1] *
                    blend)
            b = int(master_colors[idx][2] *
                    (1 -
                     blend) +
                    master_colors[min(idx +
                                  1, len(master_colors) -
                                      1)][2] *
                    blend)

            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(r, g, b, 200))

    # Effet de lueur
    img = img.filter(ImageFilter.GaussianBlur(2))

    # Découpage du centre
    mask = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        (border_width * 2,
         border_width * 2,
         size - border_width * 2 - 1,
         size - border_width * 2 - 1),
        fill=255)
    cut_center = Image.new('RGBA', img_size, (0, 0, 0, 0))
    cut_center.paste((0, 0, 0, 0), mask=mask)
    img = Image.composite(cut_center, img, mask)

    img.save(os.path.join(output_dir, 'master_border.png'))
    return img

# 7. Grandmaster


def create_grandmaster_border():
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Couleurs dégradées
    gm_colors = [(255, 215, 0), (255, 0, 0), (138, 43, 226),
                 (75, 0, 130), (148, 0, 211)]

    # Cercle principal avec dégradé
    for i in range(border_width):
        progress = i / border_width
        color_idx = progress * (len(gm_colors) - 1)
        idx = int(color_idx)
        t = color_idx - idx

        r = int(gm_colors[idx][0] * (1 - t) +
                gm_colors[min(idx + 1, len(gm_colors) - 1)][0] * t)
        g = int(gm_colors[idx][1] * (1 - t) +
                gm_colors[min(idx + 1, len(gm_colors) - 1)][1] * t)
        b = int(gm_colors[idx][2] * (1 - t) +
                gm_colors[min(idx + 1, len(gm_colors) - 1)][2] * t)

        draw.ellipse((i, i, size - i - 1, size - i - 1),
                     outline=(r, g, b, 255))

    # Cercle secondaire
    inner_offset = border_width + 10
    for i in range(5):
        draw.ellipse(
            (inner_offset + i,
             inner_offset + i,
             size - inner_offset - i - 1,
             size - inner_offset - i - 1),
            outline=(
                255,
                255,
                255,
                150 - i * 30))

    # Motif en étoile
    points = []
    star_radius = size // 2 - border_width - 15
    inner_radius = star_radius * 0.4
    for i in range(10):
        angle = math.pi * 2 * i / 10
        radius = star_radius if i % 2 == 0 else inner_radius
        x = center[0] + int(radius * math.cos(angle))
        y = center[1] + int(radius * math.sin(angle))
        points.append((x, y))

    # Dessiner l'étoile
    for i in range(len(points)):
        next_i = (i + 1) % len(points)
        draw.line(
            (points[i][0],
             points[i][1],
                points[next_i][0],
                points[next_i][1]),
            fill=(
                255,
                215,
                0,
                200),
            width=3)

    # Effet de lueur
    img = img.filter(ImageFilter.GaussianBlur(2.5))

    # Découpage du centre
    mask = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        (border_width * 2,
         border_width * 2,
         size - border_width * 2 - 1,
         size - border_width * 2 - 1),
        fill=255)
    cut_center = Image.new('RGBA', img_size, (0, 0, 0, 0))
    cut_center.paste((0, 0, 0, 0), mask=mask)
    img = Image.composite(cut_center, img, mask)

    img.save(os.path.join(output_dir, 'grandmaster_border.png'))
    return img

# 8. Mythic


def create_mythic_border():
    img = Image.new('RGBA', img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Couleurs dégradées
    mythic_colors = [(138, 43, 226), (75, 0, 130),
                     (148, 0, 211), (138, 43, 226)]

    # Bordure principale avec effet plus épais
    for i in range(border_width * 2):
        progress = i / (border_width * 2)
        color_idx = progress * (len(mythic_colors) - 1)
        idx = int(color_idx)
        t = color_idx - idx

        r = int(mythic_colors[idx][0] * (1 - t) +
                mythic_colors[min(idx + 1, len(mythic_colors) - 1)][0] * t)
        g = int(mythic_colors[idx][1] * (1 - t) +
                mythic_colors[min(idx + 1, len(mythic_colors) - 1)][1] * t)
        b = int(mythic_colors[idx][2] * (1 - t) +
                mythic_colors[min(idx + 1, len(mythic_colors) - 1)][2] * t)

        draw.ellipse((i, i, size - i - 1, size - i - 1),
                     outline=(r, g, b, 255))

    # Ajouter des runes mystiques
    for i in range(12):
        angle = i * 30
        x = center[0] + int(math.cos(math.radians(angle))
                            * (size // 2 - border_width - 15))
        y = center[1] + int(math.sin(math.radians(angle))
                            * (size // 2 - border_width - 15))

        # Dessiner un symbole runique
        rune_size = 15
        if i % 4 == 0:
            # Cercle
            draw.ellipse(
                (x - rune_size,
                 y - rune_size,
                 x + rune_size,
                 y + rune_size),
                outline=(
                    255,
                    255,
                    255,
                    200),
                width=2)
        elif i % 4 == 1:
            # Triangle
            draw.polygon([(x, y -
                           rune_size), (x +
                                        rune_size, y +
                                        rune_size), (x -
                                                     rune_size, y +
                                                     rune_size)], outline=(255, 255, 255, 200), width=2)
        elif i % 4 == 2:
            # Rune en forme de Y
            draw.line((x, y - rune_size, x, y),
                      fill=(255, 255, 255, 200), width=2)
            draw.line((x, y, x - rune_size, y + rune_size),
                      fill=(255, 255, 255, 200), width=2)
            draw.line((x, y, x + rune_size, y + rune_size),
                      fill=(255, 255, 255, 200), width=2)
        else:
            # X
            draw.line(
                (x - rune_size,
                 y - rune_size,
                 x + rune_size,
                 y + rune_size),
                fill=(
                    255,
                    255,
                    255,
                    200),
                width=2)
            draw.line(
                (x + rune_size,
                 y - rune_size,
                 x - rune_size,
                 y + rune_size),
                fill=(
                    255,
                    255,
                    255,
                    200),
                width=2)

    # Cercle lumineux intérieur
    inner_offset = border_width + 20
    for i in range(6):
        draw.ellipse(
            (inner_offset + i,
             inner_offset + i,
             size - inner_offset - i - 1,
             size - inner_offset - i - 1),
            outline=(
                200,
                100,
                255,
                200 - i * 30),
            width=1)

    # Effet de particules
    for _ in range(50):
        angle = np.random.random() * 360
        dist = np.random.random() * border_width + (size // 2 - border_width * 1.5)
        x = center[0] + int(math.cos(math.radians(angle)) * dist)
        y = center[1] + int(math.sin(math.radians(angle)) * dist)

        particle_size = np.random.randint(1, 4)
        opacity = np.random.randint(100, 255)
        draw.ellipse(
            (x - particle_size,
             y - particle_size,
             x + particle_size,
             y + particle_size),
            fill=(
                255,
                255,
                255,
                opacity))

    # Effet de lueur
    img = img.filter(ImageFilter.GaussianBlur(3))

    # Découpage du centre
    mask = Image.new('L', img_size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse(
        (border_width * 2,
         border_width * 2,
         size - border_width * 2 - 1,
         size - border_width * 2 - 1),
        fill=255)
    cut_center = Image.new('RGBA', img_size, (0, 0, 0, 0))
    cut_center.paste((0, 0, 0, 0), mask=mask)
    img = Image.composite(cut_center, img, mask)

    img.save(os.path.join(output_dir, 'mythic_border.png'))
    return img


# Créer toutes les bordures
print("Création des bordures PNG...")
create_bronze_border()
create_silver_border()
create_gold_border()
create_platinum_border()
create_diamond_border()
create_master_border()
create_grandmaster_border()
create_mythic_border()

print(f"Bordures créées avec succès dans le dossier '{output_dir}'")
