import json

"""
Ce script ouvre le fichier Json de la voirie de Paris, le parse et recherche une chaîne de caractère dans le champs "historique"
"""

with open("donnees/denominations-emprises-voies-actuelles.json") as f:
    mon_json = json.load(f)
    
for item in mon_json:
    champs = item["fields"]
    try:
        hist = champs["historique"]
    except KeyError:
        None
    # On remplace les traits d'union (les règles typographiques dans les noms de voies varient beaucoup)
    hist = hist.replace("-", " ")
    
    # Recherche d'une chaîne de caractère
    if "Saint Jean de Beauvais" in hist:
        print(f'''Trouvé ! : il s'agit de {champs["typvoie"]} {champs["nomvoie"]}. L'historique est le suivant : "{hist}"''')