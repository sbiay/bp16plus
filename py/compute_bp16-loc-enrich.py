# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import time
from time import sleep
import urllib.parse
import requests
import json

# Read recipe inputs
bp16_loc_net_prepared = dataiku.Dataset("bp16-loc_net_prepared")

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
i = 0

nouveauSet = {}

resultats = {}

for enregistrement in bp16_loc_net_prepared.iter_rows():
    if i == 0:
        for attribut in enregistrement:
            nouveauSet[attribut] = []
            nouveauSet['Coord'] = []

    for attribut in enregistrement:
        nouveauSet[attribut].append(enregistrement[attribut])

    # On assigne les attributs requêtés à des variables
    dataVille = enregistrement['Pays item']
    nomInstitution = enregistrement['Institution conservation item']

    # On cherche le nom de la ville et de l'institution dans le journal des résultats
    if resultats.get(f"{dataVille}, {nomInstitution}"):
        nouveauSet['Coord'].append(resultats[f"{dataVille}, {nomInstitution}"])
        print(f"Journal utilisé pour {i} : valeur {resultats[f'{dataVille}, {nomInstitution}']}")

    # Si le nom de la ville et de l'institution ne sont pas déjà dans le journal des résultats
    else:
        # On effectue la recherche sur le nom de l'institution en bas de casse
        nomInstitutionLow = nomInstitution.lower()
        # On découpe le nom de l'institution en mots-clés
        motscles = nomInstitutionLow.split()
        # On écrit les filtres de la requête sparql
        listeFiltres = [f'filter contains(lcase(?nomInstitution), "{mot}").' for mot in motscles]
        # On écrit la liste dans une chaîne de caractères pour pouvoir l'ajouter à la requête
        chaineFiltres = ""
        for index, filtre in enumerate(listeFiltres):
            # On n'ajoutera pas de saut de ligne pour le dernier filtre de la liste
            if index == len(listeFiltres) - 1:
                chaineFiltres += "\n" + filtre
            else:
                chaineFiltres += filtre

        queryString = '''PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
        PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n
        PREFIX p: <http://www.wikidata.org/prop/>\n
        PREFIX ps: <http://www.wikidata.org/prop/statement/>\n
        SELECT DISTINCT ?entiteInstitution ?coordonnees\n
        WHERE {\n
          ?entiteInstitution rdfs:label ?nomInstitution.\n
          ?entiteInstitution wdt:P131 ?entiteLieu.\n
          ?entiteLieu wdt:P1705 ?nomLieu.\n
          ?entiteInstitution p:P625 ?proprieteLoc.\n
          ?proprieteLoc ps:P625 ?coordonnees.\n
          filter contains(?nomLieu, "''' + dataVille + '''")\n
          ''' + chaineFiltres +'''
        }\n
        LIMIT 1'''
        requHTTP = requests.get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(queryString))

        if requHTTP.status_code == 200:
            try:
                resultat = requHTTP.json()
                # S'il y a un résultat
                if len(resultat["results"]["bindings"])>= 1:
                    donneeCoord = resultat["results"]["bindings"][0]["coordonnees"]["value"]
                    nouveauSet['Coord'].append(donneeCoord)
                    # On inscrit le résultat dans le journal des résultats
                    resultats[f"{dataVille}, {nomInstitution}"] = donneeCoord

                else:
                    resultats[f"{dataVille}, {nomInstitution}"] = "NULL"

            except json.decoder.JSONDecodeError:
                print(f"There was a problem accessing the equipment data on {enregistrement['Pays item']}.")

    for cle in nouveauSet:
        if len(nouveauSet[cle]) == i:
            nouveauSet[cle].append("NULL")

    i +=1
    """
    # Pour tester le code sur une portion limitée des enregistrements
    if i > 10:
        break

# Pour afficher les résultats de l'enrichissement
for index, enregistrement in enumerate(nouveauSet['Id BP16']):
    print(f"{index}. {nouveauSet['Id BP16'][index]} - ville : {nouveauSet['Pays item'][index]} - coordonnées : {nouveauSet['Coord'][index]}")
    """

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Pour pallier une partie des erreurs de lecture des fichiers Json, on finit par une boucle sur le journal des résultats
i = 0
for enregistrement in bp16_loc_net_prepared.iter_rows():
    # On assigne les attributs requêtés à des variables
    dataVille = enregistrement['Pays item']
    nomInstitution = enregistrement['Institution conservation item']

    # On teste si les coordonnées de l'enregistrement sont vides et si elles existent dans le journal des résultats
    if not nouveauSet['Coord'] and resultats.get(f"{dataVille}, {nomInstitution}"):
        nouveauSet['Coord'].append(resultats[f"{dataVille}, {nomInstitution}"])

    for cle in nouveauSet:
        if len(nouveauSet[cle]) == i:
            nouveauSet[cle].append("NULL")

    i +=1

    """
    # Pour tester le code sur une portion limitée des enregistrements
    if i > 10:
        break
    """

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
"""print(resultats)
for attribut in nouveauSet:
    print(attribut + ": " + str(len(nouveauSet[attribut])))
"""

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Write recipe outputs
bp16_loc_enrich_df = pd.DataFrame(nouveauSet)
bp16_loc_enrich = dataiku.Dataset("bp16_loc_enrich")
bp16_loc_enrich.write_with_schema(bp16_loc_enrich_df)