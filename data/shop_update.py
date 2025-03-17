import shared.utils.data_manager as data

import os
import requests
from github import Github
from datetime import datetime

# Remplacez par votre propre URL du dépôt GitHub
OWNER = "AlexLeDevDu22"  # Exemple : "octocat"
REPO = "Drawwy-Shop"  # Exemple : "Hello-World"
LAST_UPDATE_FILE = "data/last_update.txt"
UPDATE_DIR = "data/shop"  # Dossier où les nouveaux fichiers seront téléchargés

# Créez une instance de l'API GitHub
g = Github()

def get_last_update():
    """Lire la dernière date de mise à jour à partir du fichier"""
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, 'r') as f:
            last_update = f.read().strip()
            return datetime.strptime(last_update, "%Y-%m-%dT%H:%M:%S")
    return None

def set_last_update(update_time):
    """Enregistrer la dernière date de mise à jour dans le fichier"""
    with open(LAST_UPDATE_FILE, 'w') as f:
        f.write(update_time.strftime("%Y-%m-%dT%H:%M:%S"))

def download_file(url, file_path):
    """Télécharger un fichier depuis une URL et le sauvegarder dans un fichier local"""
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as f:
        f.write(response.content)

def check_for_shop_updates():
    """Vérifier si une mise à jour est disponible pour le dépôt GitHub"""
    repo = g.get_repo(f"{OWNER}/{REPO}")
    
    # Récupérer la dernière mise à jour du dépôt
    latest_commit = repo.get_commits()[0]  # Récupère le dernier commit
    latest_commit_time = latest_commit.commit.author.date  # Date du dernier commit
    
    # Rendre la date du dernier commit naif (supprimer le fuseau horaire)
    latest_commit_time = latest_commit_time.replace(tzinfo=None)
    
    # Comparer avec la dernière mise à jour connue
    last_update = get_last_update()
    
    if not last_update or latest_commit_time > last_update:
        print("Mise à jour détectée, téléchargement des nouveaux fichiers...")
        
        # Télécharger les fichiers du dépôt
        for content in repo.get_contents(""):
            if content.type == "file":  # Si c'est un fichier
                file_url = content.download_url
                file_path = os.path.join(UPDATE_DIR, content.name)
                download_file(file_url, file_path)
        
        # Mettre à jour la dernière date de mise à jour
        set_last_update(latest_commit_time)
        print(f"Mise à jour terminée, fichiers téléchargés dans {UPDATE_DIR}")
        data.reload()

# Créer le dossier de mise à jour si nécessaire
if not os.path.exists(UPDATE_DIR):
    os.makedirs(UPDATE_DIR)