# Drawwy - Meilleur Projet de Bretagne 1ère

## Gameplay

Il y a 2 modes, le solo et le multijoueur:

-En solo, le but est simplement de reproduire un dessin choisis au hasard parmi les thèmes présentes à l'identique.

-En multijoueur, tu es contre tes adversaires et il faut essayer de deviner un mot qu'un dessinateur choisis au hasard dans la zone au milieu de l'écran. Et si tu es dessinateur, le but est de faire deviner aux autres la phrase qui te sera attribué.

## Installation

### 1. Installer les dépendances:

```bash
pip install -r requirements.txt
pip install pygetwindow==0.0.9   # uniquement sous window
pip install pygame_emojis==0.1.1 # marche rarement sous windows(facultatif)
```

### 2. Lancez le jeu !

```bash

cd <racine_du_projet>

python sources/main.py

```

### 3. La version web!

Si vous souhaité acceder a la version en ligne du multijoueur, il suffit d'utiliser les adresses si dessous selon le serveur:

    Mastiff: "vital-mastiff-publicly.ngrok-free.app"

    Smoothly: "smoothly-on-hyena.ngrok-free.app"

    Faithful: "next-boxer-faithful.ngrok-free.app"

PS: La version web n'est accessible que lorsque le serveur est déja lancé par le jeux python
