import os

def count_lines(file_path):
    """Compte les lignes d'un fichier, en ignorant les lignes vides et les commentaires."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        # Enlever les lignes vides et les commentaires
        lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        return len(lines)

def count_code_lines_in_directory(directory):
    """Compte les lignes de code par langage dans un dossier (et ses sous-dossiers)."""
    language_lines = {}  # Dictionnaire pour stocker le nombre de lignes par langage

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # Ajouter des extensions de fichiers pour chaque langage que tu veux analyser
            if file_ext in ['.py', '.js', '.java', '.html', '.css', '.cpp', '.c', '.rb', '.php', '.go']:
                try:
                    lines = count_lines(file_path)
                    if file_ext not in language_lines:
                        language_lines[file_ext] = 0
                    language_lines[file_ext] += lines
                except Exception as e:
                    print(f"Erreur lors du traitement de {file_name}: {e}")

    return language_lines

# Exemple d'utilisation
directory = 'sources'
language_lines = count_code_lines_in_directory(directory)

# Afficher les résultats
for language, lines in language_lines.items():
    print(f"Langage {language}: {lines} lignes de code.")