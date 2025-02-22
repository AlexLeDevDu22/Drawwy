import random

sujets = [
    "Un ninja", "Un dragon", "Un caméléon", "Un magicien", "Un robot", "Une sorcière", "Un lama", "Un astronaute", 
    "Un sumo", "Un poulpe", "Un espion", "Un vampire", "Un chien", "Un chat", "Un kangourou", "Un alien", "Un pirate", 
    "Un samouraï", "Un cheval", "Un hibou", "Un dinosaure", "Une mouette", "Un hamster", "Un perroquet", "Un ananas vivant", 
    "Un pharaon", "Un monstre des marais", "Un cyclope", "Une fée", "Un yéti", "Un fantôme", "Un zombie", "Un gladiateur", 
    "Un scientifique fou", "Un chevalier", "Un esquimau", "Un capitaine de bateau", "Un pingouin", "Un singe", "Un escargot", 
    "Un avocat", "Un cactus vivant", "Un marshmallow avec des bras", "Un cochon", "Un serpent", "Un kiwi (le fruit)", 
    "Une étoile de mer", "Un iceberg", "Un brocoli", "Un ballon de foot vivant", "Une brique de lait", "Un poisson rouge", "Shreck"
]

actions = [
    "qui fait du ski", "qui danse la salsa", "qui joue de la guitare", "qui fait du surf", "qui cuisine des crêpes", 
    "qui jongle avec des poissons", "qui pilote un avion en papier", "qui joue à cache-cache", "qui chante sous la douche", 
    "qui escalade une montagne de bonbons", "qui fait du vélo sur l'eau", "qui marche sur un trampoline", "qui joue au basket", 
    "qui peint un tableau", "qui joue aux échecs avec un fantôme", "qui fabrique une fusée en carton", "qui écrit un poème", 
    "qui jongle avec des oranges", "qui essaie de réparer un robot", "qui pêche des étoiles filantes", "qui jongle avec des claçons", 
    "qui se dispute avec son miroir", "qui mange un gâteau géant", "qui saute en parachute avec un parapluie", 
    "qui essaie de voler avec des ballons", "qui fait du patin à glace sur une banane", "qui joue du piano avec ses pieds", 
    "qui construit un château en sable lunaire", "qui se bat contre son ombre", "qui se cache dans un frigo", 
    "qui essaie de parler à une plante", "qui jongle avec des téléphones", "qui essaie de dompter une vague", "qui fait un selfie avec un requin", 
    "qui fait une bataille de polochons avec un squelette", "qui boit du thé avec une pieuvre", "qui court sur un arc-en-ciel", 
    "qui fait une course de chameaux dans le désert", "qui tente de manger une pastèque entière", "qui essaie d'attraper un éclair", 
    "qui fait un duel au sabre avec un dark-vador"
]

# details = [
#     "avec un chapeau de paille", "avec un perroquet de compagnie", "avec des lunettes de soleil", "avec une pizza à la main",
#     "avec un ballon de foot", "avec des ailes de papillon", "en train de faire du skateboard", "avec une baguette magique", 
#     "avec une moustache géante", "avec un tuba et des palmes", "avec une guitare", "avec des cheveux en feu", 
#     "avec un parapluie", "avec des chaussettes dépareillées", "avec un gâteau géant", "avec un masque de super-héros", 
#     "avec des boucles d'oreilles en forme de cœur", "avec un smartphone", "avec un costume de clown", "avec un énorme sourire", 
#     "avec une cape de super-héros", "avec une tasse de chocolat chaud", "avec un appareil photo", "avec des coussins partout", 
#     "avec des lunettes 3D", "avec des ballons gonflés", "avec une grosse barbe", "avec un casque de vélo", 
#     "avec une cape en écharpe", "avec un t-shirt fluo", "avec des extraterrestes autour", "avec un costume de pirate", 
#     "avec un sac à dos énorme", "avec un drone volant autour", "avec une pizza géante", "avec un cheval en bois", 
#     "avec des paillettes partout", "avec un sac à main", "avec des écouteurs géants", "avec un ballon de baudruche", 
#     "avec des lunettes à moustache", "avec une couronne en papier", "avec un chat sur l'épaule", "avec un cactus", 
#     "avec des palmes géantes", "avec un tapis volant", "avec un soleil en fond", "avec des chaussons en forme d'animaux", 
#     "avec des tatouages temporaires", "avec des pattes de lapin", "avec un chaton", "avec une tasse de thé", 
#     "avec des étoiles autour", "avec une fusée en arrière-plan", "avec un sac de bonbons", "avec un oreiller", 
#     "avec des lunettes de ski", "avec une écharpe en laine", "avec une raquette de tennis", "avec un vélo sur le dos", 
#     "avec une poignée de fleurs", "avec un bouquet de roses", "avec des chocolats", "avec des glaces", "avec des feux d'artifice",
#     "avec des guirlandes", "avec un skate", "avec une bouée", "avec des chaussettes rigolotes", "avec un coussin"
# ]


def new_sentence():
    global sujets, actions, details

    sujet = random.choice(sujets)
    action = random.choice(actions)
    #detail = random.choice(details)
    sentence = f"{sujet} {action}"
        
    return sentence
