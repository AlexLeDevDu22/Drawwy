import shared.utils.data_manager as data
from shared.tools import is_connected

import os
import requests
from github import Github
from datetime import datetime, timedelta

# Remplacez par votre propre URL du dépôt GitHub
OWNER = "AlexLeDevDu22"  # Exemple : "octocat"
REPO = "Drawwy-Shop"  # Exemple : "Hello-World"
LAST_CHECK_FILE = "data/last_update_checked.txt"
UPDATE_DIR = "data/shop"  # Dossier où les nouveaux fichiers seront téléchargés

# Créez une instance de l'API GitHub
g = Github()

def get_last_check():
    """Renvoie la date de la dernière mise à jour connue (None si jamais)"""
    if os.path.exists(LAST_CHECK_FILE):
        with open(LAST_CHECK_FILE, 'r') as f:
            last_check = f.read().strip()
            if last_check != "":
                return datetime.strptime(last_check, "%Y-%m-%dT%H:%M:%S")
    return None


def set_last_check(update_time):
    """Enregistrer la dernière date de mise à jour dans le fichier"""
    with open(LAST_CHECK_FILE, 'w') as f:
        f.write(update_time.strftime("%Y-%m-%dT%H:%M:%S"))


def download_file(url, file_path):
    """Télécharge un fichier depuis une URL et l'enregistre à un emplacement local.

    Args:
        url (str): URL du fichier à télécharger.
        file_path (str): Chemin local où enregistrer le fichier.
    Raises:
        requests.exceptions.RequestException: Si la requête échoue (par exemple si la
            connexion internet est perdue).
    """
    response = requests.get(url)
    response.raise_for_status()
    with open(file_path, 'wb') as f:
        f.write(response.content)


def download_repo_contents(repo, path="", local_dir=UPDATE_DIR):
    """
    Télécharge le contenu d'un dépôt GitHub spécifié dans un répertoire local.

    Parcourt de manière récursive les fichiers et dossiers du dépôt à partir d'un chemin donné et
    les télécharge dans un répertoire local spécifié. Le chemin local de chaque fichier/dossier
    téléchargé est renvoyé.

    Args:
        repo (github.Repository.Repository): Instance du dépôt GitHub à partir duquel télécharger.
        path (str): Chemin dans le dépôt à partir duquel commencer le téléchargement (par défaut "").
        local_dir (str): Répertoire local où stocker les fichiers téléchargés (par défaut UPDATE_DIR).

    Returns:
        list: Liste des chemins locaux de tous les fichiers et dossiers téléchargés.

    Raises:
        github.GithubException: Si la récupération du contenu échoue.
    """
    contents = repo.get_contents(path)  # Liste des fichiers/dossiers à `path`

    all_paths = []

    for content in contents:
        file_path = os.path.join(
            local_dir, content.path)  # Crée le chemin local

        if content.type == "dir":
            # Si c'est un dossier, le créer et continuer récursivement
            os.makedirs(file_path, exist_ok=True)
            all_paths += download_repo_contents(repo, content.path, local_dir)
            all_paths.append(file_path)

        elif content.type == "file":
            # Si c'est un fichier, le télécharger
            print(f"Téléchargement : {content.path}")
            download_file(content.download_url, file_path)
            all_paths.append(file_path)

    return all_paths


def check_for_shop_updates():
    """Vérifie si une mise à jour du shop est disponible sur le dépôt GitHub.

    Si une mise à jour est disponible, télécharge les nouveaux fichiers dans le
    dossier `UPDATE_DIR` et met à jour la date de la dernière mise à jour.

    Si la connexion internet est perdue, sort sans faire quoi que ce soit.

    Appelé une fois par jour par le thread `updater`.
    """
    if not is_connected():
        return


    # Comparer avec la dernière mise à jour connue
    last_check = get_last_check()

    if last_check and last_check + timedelta(days=1) > datetime.now():
        return

    repo = g.get_repo(f"{OWNER}/{REPO}")
    # Récupérer la dernière mise à jour du dépôt
    latest_commit = repo.get_commits()[0]
    latest_commit_time = latest_commit.commit.author.date.replace(tzinfo=None)

    if not last_check or latest_commit_time > last_check:
        print("Mise à jour détectée, téléchargement des nouveaux fichiers...")

        # Télécharger récursivement tous les fichiers/dossiers
        all_path = download_repo_contents(repo)

        print(all_path)
        for p in os.listdir(UPDATE_DIR):
            p = os.path.join(UPDATE_DIR, p)
            if p not in all_path and os.path.isfile(p):
                os.remove(p)

        # Mettre à jour la dernière date de mise à jour
        print(f"Mise à jour terminée, fichiers téléchargés dans {UPDATE_DIR}")

    set_last_check(datetime.now())
    data.reload()


# Créer le dossier de mise à jour si nécessaire
if not os.path.exists(UPDATE_DIR):
    os.makedirs(UPDATE_DIR)
