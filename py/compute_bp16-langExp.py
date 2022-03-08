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

# On boucle sur les enregistrements (les lignes) du jeu de données de départ
for enregistrement in bp16_export_primaire.iter_rows():
    # Pour l'index 0, on récupère tous les attributs du jeu de données de départ
    if i == 0:
        for attribut in enregistrement:
            nouveauSet[attribut] = []

            # On crée un nouvel attribut pour le nouveau jeu de données
            nouveauSet['langueExpressionISO'] = []

    # On récupère toutes les valeurs d'attributs du jeu de départ pour les charger dans le nouveau jeu
    for attribut in enregistrement:
        nouveauSet[attribut].append(enregistrement[attribut])

    # On construit une URI DataBnF à partir du numéro ark contenu dans l'URI BP16 de la manifestation
    uriDataManif = f"http://data{enregistrement['?uriManif'][13:43]}#about"
    
    # On écrit la requête Sparql
    queryString = '''SELECT DISTINCT ?langue
WHERE {<''' + uriDataManif + '''> <http://rdvocab.info/RDARelationshipsWEMI/expressionManifested> ?uriexpression.
?uriexpression <http://purl.org/dc/terms/language> ?langue.
} LIMIT 1'''
    
    # On injecte la requête Sparql dans une requête HTTP grâce à la fonction urllib.parse.quote
    requHTTP = requests.get("https://data.bnf.fr/sparql?format=json&query=" + urllib.parse.quote(queryString))
    
    # On récupère le résultat au format Json
    resultat = requHTTP.json()
    
    # On parse le résultat pour récupérer la valeur recherchée
    donnee = resultat["results"]["bindings"][0]["langue"]["value"]

    # On remplit la valeur du nouvel attribut pour l'enregistrement courant
    nouveauSet['langueExpressionISO'].append(donnee)

    # Pour tester le code sur une portion limitée des enregistrements
    i += 1
    if i > 50:
        break

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# On imprime en test le nombre de valeur pour chaque attribut (il doit absolument être identique partout)
for attribut in nouveauSet:
    print(attribut + ": " + str(len(nouveauSet[attribut])))

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Compute recipe outputs from inputs
# TODO: Replace this part by your actual code that computes the output, as a Pandas dataframe
# NB: DSS also supports other kinds of APIs for reading and writing data. Please see doc.

bp16_langExp_df = pd.DataFrame(nouveauSet)

# Write recipe outputs
bp16_langExp = dataiku.Dataset("bp16-langExp")
bp16_langExp.write_with_schema(bp16_langExp_df)