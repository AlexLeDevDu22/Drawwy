pip freeze > requirements.txt

Si on lance le script pour la première fois sur l'ordi, ya un long chargement



Pour Pull depuis le lycée: 
installer git(dans le powershell):
    iwr -useb get.scoop.sh | iex
    scoop install git

se co gitlab:
    git config --global --get-all credential.helper
    git config --global --add credential.helper "store --file ~/.git-credentials"

    git remote add nsi https://AlexLeDevDu22:glpat-37iFxwP77FXmyHNtLMvf@gitlab.com/maxence.tardivel.mt/truc-nsi
    git remote set-url nsi https://AlexLeDevDu22:glpat-37iFxwP77FXmyHNtLMvf@gitlab.com/maxence.tardivel.mt/truc-nsi
    git pull nsi main
    git branch checkout main