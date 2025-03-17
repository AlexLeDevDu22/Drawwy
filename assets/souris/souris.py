from PIL import Image, ImageDraw
import os
import math

def create_funny_cursor(design_type, size=32):
    """
    Crée un curseur de souris amusant en PNG
    
    Args:
        design_type (str): Type de design ("cat", "alien", "robot", "ghost", "unicorn")
        size (int): Taille du curseur en pixels
        output_dir (str): Dossier de sortie
    
    Returns:
        str: Chemin du fichier sauvegardé
    """
    # Créer une image avec transparence
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Point chaud du curseur (hotspot)
    hotspot = (0, 0)
    
    # Nom du fichier de sortie
    file_name = f"cursor_{design_type}.png"
    
    # Dessiner différents curseurs selon le design choisi
    if design_type == "cat":
        # Curseur chat
        # Tête
        draw.ellipse((5, 5, size-5, size-5), fill=(255, 200, 150, 255), outline=(0, 0, 0, 255))
        
        # Oreilles
        draw.polygon([(5, 10), (0, 0), (15, 5)], fill=(255, 200, 150, 255), outline=(0, 0, 0, 255))
        draw.polygon([(size-5, 10), (size, 0), (size-15, 5)], fill=(255, 200, 150, 255), outline=(0, 0, 0, 255))
        
        # Yeux
        eye_size = size // 10
        draw.ellipse((size//3 - eye_size, size//3 - eye_size, 
                      size//3 + eye_size, size//3 + eye_size), 
                     fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        draw.ellipse((2*size//3 - eye_size, size//3 - eye_size, 
                      2*size//3 + eye_size, size//3 + eye_size), 
                     fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
        
        # Pupilles
        pupil_size = eye_size // 2
        draw.ellipse((size//3 - pupil_size, size//3 - pupil_size, 
                      size//3 + pupil_size, size//3 + pupil_size), 
                     fill=(0, 0, 0, 255))
        draw.ellipse((2*size//3 - pupil_size, size//3 - pupil_size, 
                      2*size//3 + pupil_size, size//3 + pupil_size), 
                     fill=(0, 0, 0, 255))
        
        # Nez
        draw.polygon([(size//2, size//2), (size//2 - size//10, 2*size//3), 
                      (size//2 + size//10, 2*size//3)], 
                     fill=(255, 150, 150, 255), outline=(0, 0, 0, 255))
        
        # Moustaches
        draw.line([(size//3, size//2), (2, size//2 - size//10)], fill=(0, 0, 0, 255), width=1)
        draw.line([(size//3, size//2), (2, size//2)], fill=(0, 0, 0, 255), width=1)
        draw.line([(size//3, size//2), (2, size//2 + size//10)], fill=(0, 0, 0, 255), width=1)
        
        draw.line([(2*size//3, size//2), (size-2, size//2 - size//10)], fill=(0, 0, 0, 255), width=1)
        draw.line([(2*size//3, size//2), (size-2, size//2)], fill=(0, 0, 0, 255), width=1)
        draw.line([(2*size//3, size//2), (size-2, size//2 + size//10)], fill=(0, 0, 0, 255), width=1)
        
        # Bouche
        draw.arc((size//3, size//2, 2*size//3, 3*size//4), 0, 180, fill=(0, 0, 0, 255), width=1)
        
        hotspot = (size//2, size//2)
    
    elif design_type == "alien":
        # Curseur alien
        # Tête ovale
        draw.ellipse((5, 8, size-5, size-2), fill=(150, 255, 150, 255), outline=(0, 0, 0, 255))
        
        # Grands yeux
        eye_size = size // 6
        draw.ellipse((size//3 - eye_size, size//3 - eye_size, 
                      size//3 + eye_size, size//3 + eye_size), 
                     fill=(0, 0, 0, 255))
        draw.ellipse((2*size//3 - eye_size, size//3 - eye_size, 
                      2*size//3 + eye_size, size//3 + eye_size), 
                     fill=(0, 0, 0, 255))
        
        # Reflets dans les yeux
        highlight_size = eye_size // 3
        draw.ellipse((size//3 - highlight_size, size//3 - highlight_size, 
                      size//3 + highlight_size//2, size//3 + highlight_size//2), 
                     fill=(255, 255, 255, 255))
        draw.ellipse((2*size//3 - highlight_size, size//3 - highlight_size, 
                      2*size//3 + highlight_size//2, size//3 + highlight_size//2), 
                     fill=(255, 255, 255, 255))
        
        # Petite bouche
        draw.ellipse((size//2 - size//10, 2*size//3, 
                      size//2 + size//10, 2*size//3 + size//10), 
                     fill=(0, 0, 0, 255))
        
        # Antennes
        draw.line([(size//3, 8), (size//4, 0)], fill=(0, 0, 0, 255), width=2)
        draw.line([(2*size//3, 8), (3*size//4, 0)], fill=(0, 0, 0, 255), width=2)
        
        hotspot = (size//2, size//2)
    
    elif design_type == "robot":
        # Curseur robot
        # Tête carrée
        draw.rectangle((5, 5, size-5, size-5), fill=(200, 200, 200, 255), outline=(0, 0, 0, 255), width=2)
        
        # Yeux rectangulaires
        draw.rectangle((size//3 - size//10, size//3, 
                        size//3 + size//10, size//3 + size//8), 
                      fill=(0, 0, 255, 255), outline=(0, 0, 0, 255))
        draw.rectangle((2*size//3 - size//10, size//3, 
                        2*size//3 + size//10, size//3 + size//8), 
                      fill=(0, 0, 255, 255), outline=(0, 0, 0, 255))
        
        # Bouche mécanique
        for i in range(3):
            y_pos = size//2 + i * (size//10)
            draw.line([(size//3, y_pos), (2*size//3, y_pos)], fill=(0, 0, 0, 255), width=1)
        
        # Antenne
        draw.rectangle((size//2 - size//20, 2, size//2 + size//20, 5), fill=(100, 100, 100, 255))
        draw.ellipse((size//2 - size//10, 0, size//2 + size//10, size//5), fill=(255, 0, 0, 255))
        
        # Boulons
        bolt_size = size // 20
        for x, y in [(10, 10), (size-10, 10), (10, size-10), (size-10, size-10)]:
            draw.ellipse((x - bolt_size, y - bolt_size, 
                          x + bolt_size, y + bolt_size), 
                        fill=(50, 50, 50, 255))
        
        hotspot = (size//2, size//2)
    
    elif design_type == "ghost":
        # Curseur fantôme
        # Corps du fantôme
        draw.ellipse((5, 5, size-5, size-15), fill=(255, 255, 255, 210), outline=(200, 200, 220, 255), width=1)
        
        # Base ondulée
        wave_height = size // 8
        for i in range(3):
            x1 = 5 + i * ((size-10) // 3)
            x2 = 5 + (i+1) * ((size-10) // 3)
            y1 = size - 15
            y2 = size - 5
            points = [
                (x1, y1),
                ((x1+x2)//2, y2),
                (x2, y1)
            ]
            draw.polygon(points, fill=(255, 255, 255, 210), outline=(200, 200, 220, 255))
        
        # Yeux
        eye_size = size // 12
        draw.ellipse((size//3 - eye_size, size//3, 
                      size//3 + eye_size, size//3 + 2*eye_size), 
                     fill=(0, 0, 0, 255))
        draw.ellipse((2*size//3 - eye_size, size//3, 
                      2*size//3 + eye_size, size//3 + 2*eye_size), 
                     fill=(0, 0, 0, 255))
        
        # Bouche
        mouth_size = size // 5
        draw.arc((size//2 - mouth_size, size//2, 
                 size//2 + mouth_size, size//2 + mouth_size), 
                0, 180, fill=(0, 0, 0, 255), width=1)
        
        hotspot = (size//2, size//3)
    
    elif design_type == "unicorn":
        # Curseur licorne
        # Tête
        draw.ellipse((8, 8, size-8, size-8), fill=(255, 230, 250, 255), outline=(0, 0, 0, 255))
        
        # Corne
        draw.polygon([(size//2, 8), (size//2 - size//15, 0), (size//2 + size//15, 0)], 
                    fill=(255, 215, 0, 255), outline=(0, 0, 0, 255))
        
        # Yeux
        eye_size = size // 12
        draw.ellipse((size//3 - eye_size, size//3, 
                      size//3 + eye_size, size//3 + eye_size), 
                     fill=(0, 0, 0, 255))
        draw.ellipse((2*size//3 - eye_size, size//3, 
                      2*size//3 + eye_size, size//3 + eye_size), 
                     fill=(0, 0, 0, 255))
        
        # Sourire
        draw.arc((size//3, size//2, 2*size//3, 2*size//3), 
                0, 180, fill=(0, 0, 0, 255), width=1)
        
        # Crinière colorée
        colors = [(255, 0, 0, 255), (255, 165, 0, 255), (255, 255, 0, 255), 
                  (0, 255, 0, 255), (0, 0, 255, 255), (128, 0, 128, 255)]
        for i, color in enumerate(colors):
            angle = 180 + i * 30
            x1 = size//2
            y1 = size//2
            length = size//3
            x2 = int(x1 + length * math.cos(math.radians(angle)))
            y2 = int(y1 + length * math.sin(math.radians(angle)))
            draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        
        hotspot = (size//2, size//3)
    
    # Sauvegarder l'image
    img.save(file_name)
    
    # Créer un fichier hotspot pour certains systèmes
    with open(f"{file_name}.info", "w") as f:
        f.write(f"hotspot={hotspot[0]},{hotspot[1]}")
    
    print(f"Curseur '{design_type}' créé: {file_name}")
    return file_name

def create_all_funny_cursors(size=32):
    """Crée tous les curseurs amusants disponibles"""
    designs = ["cat", "alien", "robot", "ghost", "unicorn"]
    for design in designs:
        create_funny_cursor(design, size)

if __name__ == "__main__":
    create_all_funny_cursors(64)  # Crée des curseurs de taille 64x64