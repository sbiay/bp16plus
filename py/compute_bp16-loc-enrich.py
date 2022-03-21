# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
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

    # On teste si le nom de la ville est déjà dans le journal des résultats
    if resultats.get(f"{dataVille}, {nomInstitution}"):
        nouveauSet['Coord'].append(resultats[f"{dataVille}, {nomInstitution}"])

    else:
        # On effectue la recherche sur le nom de l'institution en bas de casse
        nomInstitutionLow = nomInstitution.lower()
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
          filter contains(lcase(?nomInstitution), "''' + nomInstitutionLow + '''")\n
        }\n
        LIMIT 1'''
        requHTTP = requests.get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(queryString))
        try:
            resultat = requHTTP.json()
            # S'il y a un résultat
            if len(resultat["results"]["bindings"])>= 1:
                donneeCoord = resultat["results"]["bindings"][0]["coordonnees"]["value"]
                nouveauSet['Coord'].append(donneeCoord)
                # On inscrit le résultat dans le journal des résultats
                resultats[f"{dataVille}, {nomInstitution}"] = donneeCoord

        except json.decoder.JSONDecodeError:
            print(f"There was a problem accessing the equipment data on {enregistrement['Pays item']}.")
    for cle in nouveauSet:
        if len(nouveauSet[cle]) == i:
            nouveauSet[cle].append("")

    i +=1

    # Pour tester le code sur une portion limitée des enregistrements
    if i > 15:
        break
# Pour afficher les résultats de l'enrichissement
for index, enregistrement in enumerate(nouveauSet['Id BP16']):
    print(f"{index}. {nouveauSet['Id BP16'][index]} - ville : {nouveauSet['Pays item'][index]} - coordonnées : {nouveauSet['Coord'][index]}")

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
            nouveauSet[cle].append("")

    i +=1

    # Pour tester le code sur une portion limitée des enregistrements
    if i > 15:
        break

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
print(resultats)
for attribut in nouveauSet:
    print(attribut + ": " + str(len(nouveauSet[attribut])))

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Write recipe outputs
bp16_loc_enrich_df = pd.DataFrame(nouveauSet)
bp16_loc_enrich = dataiku.Dataset("bp16-loc-enrich")
bp16_loc_enrich.write_with_schema(bp16_loc_enrich_df)