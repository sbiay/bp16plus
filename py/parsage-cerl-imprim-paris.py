import csv
import json

# On récupère le contenu du fichier Json
with open("donnees/cerl-imprim-paris.json") as jsonf:
    cerlJson = json.load(jsonf)
    
# On ouvre un fichier CSV pour exporter les résultats
with open("donnees/cerl-imprim-paris.csv", mode="w") as csvf:
    entetes = ["idCERL", "idDataBNF", ]
    ecriveur = csv.DictWriter(csvf, fieldnames=entetes)