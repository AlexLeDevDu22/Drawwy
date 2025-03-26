import os
import json

# Charger le JSON depuis un fichier
json_path = "data.json"  # Mets ici le chemin de ton fichier JSON
with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Parcourir chaque catégorie
for category in data:
    folder_path = "assets/soloImages/"+category["path"]  # Récupérer le chemin du dossier

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # Lister les fichiers images (filtrer les fichiers pour ne garder que .png, .jpg, etc.)
        images = sorted(
            [f for f in os.listdir(folder_path) if f.endswith((".png", ".jpg", ".jpeg"))]
        )

        # Mettre à jour la liste des images dans la catégorie
        category["images"] = [
            {"index": i, "path": img, "stars": 0, "num_try": 0} for i, img in enumerate(images)
        ]
    else:
        print(f"⚠️ Dossier introuvable : {folder_path}")

# Sauvegarder le JSON mis à jour
with open(json_path, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2, ensure_ascii=False)

print("✅ JSON mis à jour avec les images trouvées !")
