from tkinter import *
import csv
with open("cities.csv", newline="", encoding="utf-8") as fichier_csv:
    lecteur = csv.reader(fichier_csv)
    next(lecteur)  # Sauter l'en-tête
    noms = [ligne[3] for ligne in lecteur]  # Récupérer la première colonne


def petitFormat():
    print("Petit format sélectionné")  # Action du menu

def calcul():
    depart = rep_depart.get()
    arrive = rep_arrive.get()
    depart = depart.lower()
    arrive = arrive.lower()
    if depart in noms:
        if arrive in noms:
            print(f"Vous partez de {depart} pour vous rendre sur {arrive}")
            request = [depart,arrive]
            print(request)
        else:
            print("Votre destination n'éxiste pas")
    else:
        print("Votre point de départ n'éxiste pas")


with open("cities.csv", newline="", encoding="utf-8") as fichier_csv:
    lecteur = csv.reader(fichier_csv)
    next(lecteur)  # Sauter l'en-tête
    noms = [ligne[3] for ligne in lecteur]  # Récupérer la première colonne



# Initialisation de la fenêtre
root = Tk()
root.geometry("900x600")


#Choix de la locomotion
choix_locomotion = Menubutton(root, text="Locomotion", font=("Arial", 14), relief=RAISED, padx=20, pady=10)
choix_locomotion.menu = Menu(choix_locomotion, tearoff=0)  # Création du menu

# Ajout d'options au menu
choix_locomotion.menu.add_command(label="Voitures", command=petitFormat)


choix_locomotion.config(menu=choix_locomotion.menu)


choix_locomotion.place(relx=0.5, rely=0.5, anchor=CENTER)

ask_depart = Label(root, text="D'où part tu?")
rep_depart = Entry(root)
ask_arrive = Label(root, text="D'où part tu?")
rep_arrive = Entry(root)
valider=Button(root, text="Valider",command=calcul)

ask_depart.grid()
rep_depart.grid()
ask_arrive.grid()
rep_arrive.grid()
valider.grid()

root.mainloop()
