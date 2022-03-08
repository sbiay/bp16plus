# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import urllib.parse
import requests

# On charge le jeu de données de départ
bp16_export_primaire = dataiku.Dataset("bp16-export-primaire")

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# On initie un index
i = 0

# On initie le nouveau jeu de données pour récupérer les données enrichies
nouveauSet = {}

# On initie un dictionnaire pour stocker les données enrichies, afin de ne pas réitérer les mêmes requêtes
# avec comme clé l'identifiant ark
# et comme valeur la donnée récoltée
resultats = {}

# On boucle sur les enregistrements (les lignes) du jeu de données de départ
for enregistrement in bp16_export_primaire.iter_rows():
    # Pour l'index 0, on récupère tous les attributs du jeu de données de départ
    if i == 0:
        for attribut in enregistrement:
            nouveauSet[attribut] = []

            # On crée un nouvel attribut pour le nouveau jeu de données
            nouveauSet['langueExpressionISO'] = []

    # On récupère toutes les valeurs du jeu de départ pour les charger dans le nouveau jeu
    for attribut in enregistrement:
        nouveauSet[attribut].append(enregistrement[attribut])

    # On vérifie que l'enrichissement de la donnée n'ait pas déjà été fait
    # en cherchant l'idenfiant ark dans le journal des résultats
    ark = enregistrement['?uriManif'][21:-2]
    if resultats.get(ark):
        # Si oui, on ajoute la donnée au nouveau set à partir du journal des résultats
        nouveauSet['langueExpressionISO'].append(resultats[ark])
    else:
        # On construit une URI DataBnF à partir du numéro ark contenu dans l'URI BP16 de la manifestation
        uriDataManif = f"http://data.bnf.fr/{ark}#about"

        # On écrit la requête Sparql
        queryString = '''SELECT DISTINCT ?langue
    WHERE {<''' + uriDataManif + '''> <http://rdvocab.info/RDARelationshipsWEMI/expressionManifested> ?uriexpression.
    ?uriexpression <http://purl.org/dc/terms/language> ?langue.
    } LIMIT 1'''

        # On injecte la requête Sparql dans une requête HTTP grâce à la fonction urllib.parse.quote
        requHTTP = requests.get("https://data.bnf.fr/sparql?format=json&query=" + urllib.parse.quote(queryString))

        # On récupère le Json dans un try afin d'éviter les problèmes de décodage de fichier
        try:
            resultat = requHTTP.json()

            # On parse le résultat pour récupérer la valeur recherchée
            if len(resultat["results"]["bindings"]) == 1:
                donnee = resultat["results"]["bindings"][0]["langue"]["value"]


            # On remplit la valeur du nouvel attribut pour l'enregistrement courant
            nouveauSet['langueExpressionISO'].append(donnee)

        except json.decoder.JSONDecodeError:
            print(f"There was a problem accessing the equipment data on {enregistrement['?uriManif']}.")

        # TRES IMPORTANT : s'il n'y a pas de résultat dans le contenu parsé, on ajoute un NULL
        # car la cohérence des données repose sur l'absence de vide
        for cle in nouveauSet:
            if len(nouveauSet[cle]) == i:
                nouveauSet[cle].append("NULL")

        # On inscrit l'enrichissement dans le journal des résultats
        resultats[ark] = donnee
    
    # On implémente l'index suivant
    i += 1

    # Pour tester le code sur une portion limitée des enregistrements
    if i > 10:
        break

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# On imprime en test le nombre de valeur pour chaque attribut (il doit absolument être identique partout)
for attribut in nouveauSet:
    print(attribut + ": " + str(len(nouveauSet[attribut])))
    
print(resultats)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# On implémente les résultats dans un objet DataFrame
bp16_langExp_df = pd.DataFrame(nouveauSet)

# On écrit tout cela dans le dataset de sortie
bp16_langExp = dataiku.Dataset("bp16-langExp")
bp16_langExp.write_with_schema(bp16_langExp_df)