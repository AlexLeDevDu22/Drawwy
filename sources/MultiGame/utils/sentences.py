import random

sujets = [
    "Un ninja",
    "Un dragon",
    "Un caméléon",
    "Un magicien",
    "Un robot",
    "Une sorcière",
    "Un lama",
    "Un astronaute",
    "Un poulpe",
    "Un espion",
    "Un vampire",
    "Un chien",
    "Un chat",
    "Un kangourou",
    "Un alien",
    "Un pirate",
    "Un cheval",
    "Un hibou",
    "Un dinosaure",
    "Un hamster",
    "Un perroquet",
    "Shrek",
    "Un cyclope",
    "Une fée",
    "Un fantôme",
    "Un zombie",
    "Un docteur",
    "Un chevalier",
    "Un pingouin",
    "Un singe",
    "Un escargot",
    "Un avocat",
    "Un cactus",
    "Un marshmallow",
    "Un cochon",
    "Un serpent",
    "Un kiwi",
    "Une étoile de mer",
    "Un ballon de foot",
    "Une brique de lait",
    "Un poisson rouge",
    "Un hamburger",
    "Un hot-dog",
    "Une chaussure",
    "Un aspirateur",
    "Une tasse de café",
    "Un crabe",
    "Un mouton",
    "Un bonhomme en pain d’épices",
    "Une carotte",
    "Un sushi",
    "Une guitare",
    "Un téléphone ",
    "Une pizza",
    "Un éléphant",
    "Une girafe",
    "Un ours",
    "Un kangourou",
    "Un caméléon",
]

actions = [
    "qui fait du ski",
    "qui danse",
    "qui joue de la guitare",
    "qui fait du surf",
    "qui cuisine des crêpes",
    "qui jongle avec des poissons",
    "qui lance un avion en papier",
    "qui se cache derrière un arbre",
    "qui chante",
    "qui escalade une montagne",
    "qui fait du vélo",
    "sur un trampoline",
    "qui joue au basket",
    "qui peint",
    "qui joue aux échecs",
    "qui mange une pastèque",
    "qui jongle avec des oranges",
    "qui construit un robot",
    "qui regarde des étoiles filantes",
    "qui jongle avec des glaçons",
    "qui mange son télephone",
    "qui mange un gâteau",
    "qui saute en parachute",
    "qui vole avec des ballons",
    "qui glice sur une banane",
    "qui joue du piano",
    "qui joue du saxophone",
    "qui construit un château en sable",
    "qui se bat contre son ombre",
    "qui rentre dans un frigo",
    "qui parle à une plante",
    "qui jongle avec des téléphones",
    "qui surf sur une gauffre",
    "qui fait un selfie",
    "qui boit du thé",
    "qui court sur un arc-en-ciel",
    "qui fait une course de chameaux",
    "qui mange une pastèque",
    "qui se prend un éclair",
    "qui se bat contre Dark Vador",
    "qui joue au foot avec une pastèque",
    "qui dort sur un nuage",
    "qui fait une bataille de boules de neige avec un pingouin",
    "qui danse avec une méduse",
    "qui mange des spaghettis",
    "qui fait une course contre un escargot",
    "sur la lune",
    "qui lit un livre dans l’espace",
    "qui fait du trampoline sur la Lune",
]


def new_sentence():
    """
    Return a new sentence composed of a random subject and action.

    Returns:
        str: a sentence of the form "<sujet> <action>".
    """
    global sujets, actions, details

    sujet = random.choice(sujets)
    action = random.choice(actions)
    # detail = random.choice(details)
    sentence = f"{sujet} {action}"

    return sentence
