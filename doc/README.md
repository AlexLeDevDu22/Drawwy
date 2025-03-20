pip freeze > doc/requirements.txt

& doc/install-requirements.ps1

autopep8 --in-place --aggressive --aggressive --recursive . --exclude .venv,.git,.vscode

Si on lance le script pour la première fois sur l'ordi, ya un long chargement

SUR WINDOW!!!!
pip install aiohttp

Pour Pull depuis le lycée:
installer git(dans le powershell):
iwr -useb get.scoop.sh | iex
scoop install git

se co gitlab:
git config --global --get-all credential.helper
git config --global --add credential.helper "store --file ~/.git-credentials"
git config --global user.name "FIRST_NAME LAST_NAME"
git config --global user.email "MY_NAME@example.com"

    git remote add nsi https://AlexLeDevDu22:glpat-37iFxwP77FXmyHNtLMvf@gitlab.com/maxence.tardivel.mt/truc-nsi
    git remote set-url nsi https://AlexLeDevDu22:glpat-37iFxwP77FXmyHNtLMvf@gitlab.com/maxence.tardivel.mt/truc-nsi
    git pull nsi main
    git branch checkout main
