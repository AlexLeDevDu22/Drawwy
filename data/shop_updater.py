import shared.utils.data_manager as data
from shared.tools import is_connected

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
            if last_update != "":
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

def download_repo_contents(repo, path="", local_dir=UPDATE_DIR):
    """Télécharge récursivement tous les fichiers du repo"""
    contents = repo.get_contents(path)  # Liste des fichiers/dossiers à `path`
    
    for content in contents:
        file_path = os.path.join(local_dir, content.path)  # Crée le chemin local
        
        if content.type == "dir":  
            # Si c'est un dossier, le créer et continuer récursivement
            os.makedirs(file_path, exist_ok=True)
            download_repo_contents(repo, content.path, local_dir)  
        
        elif content.type == "file":  
            # Si c'est un fichier, le télécharger
            print(f"Téléchargement : {content.path}")
            download_file(content.download_url, file_path)

def check_for_shop_updates():
    """Vérifier si une mise à jour est disponible pour le dépôt GitHub"""
    if not is_connected():
        return

    repo = g.get_repo(f"{OWNER}/{REPO}")
    
    # Récupérer la dernière mise à jour du dépôt
    latest_commit = repo.get_commits()[0]
    latest_commit_time = latest_commit.commit.author.date.replace(tzinfo=None)
    
    # Comparer avec la dernière mise à jour connue
    last_update = get_last_update()
    
    if not last_update or latest_commit_time > last_update:
        print("Mise à jour détectée, téléchargement des nouveaux fichiers...")
        
        # Télécharger récursivement tous les fichiers/dossiers
        download_repo_contents(repo)
        
        # Mettre à jour la dernière date de mise à jour
        set_last_update(latest_commit_time)
        print(f"Mise à jour terminée, fichiers téléchargés dans {UPDATE_DIR}")
        data.reload()


# Créer le dossier de mise à jour si nécessaire
if not os.path.exists(UPDATE_DIR):
    os.makedirs(UPDATE_DIR)