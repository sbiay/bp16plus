# Regex devoir données, modifs Zoé:

La colonne **?localisation** contient, en une seule fois, des informations concernant la *ville* et l'*institution* où sont conservés les ouvrages, ainsi que leur *cote* et leur *état*.

Pour chaque information, une nouvelle colonne est créée et les données sont déplacées de la colonnes principale vers la colonne adaptée.



## Etape 1: la colonne Etat item

1. D'abord, extraire les données avec le *extract with regular expression* et les importer dans une nouvelle colonne **Etat item** en utilisant cette regex: `(\(?état.*\)?)`
2. Puis retirer ces données de la colonne **?localisation** avec la même regex.
3. Nettoyer les données de la colonne **Etat item** en retirant les parenthèses avec un *find and replace*
4. Renommer la colonne en **Etat item** au lieu du **Etat item1** automatique


## Etape 2: la colonne Institution de conservation

1. Depuis la colonne **?localisation**, même extraction des données avec cette expression régulière: `[,|.] (.*)$` vers la nouvelle colonne **Institution conservation item**
2. Nettoyage des chaînes de caractères: utiliser la regex: `(.*\), )` à ne remplacer par rien dans la colonne **Institutio conservation item**





## Etape 3: la colonne Ville de conservation

1. Depuis la colonne **?localisation**, même extraction des données avec cette expression régulière: `^(.*)[,|(. )]` vers la nouvelle colonne **Ville item**
2. Nettoyage des données: faire un *find and replace* avec l'expression régulière `,.*`
3. Renommer la colonne sans le 1 automatique

OU, plus simple:
1. Renommer la colonne **?localisation** en **Pays item**
2. Nettoyage des données: faire un *find and replace* avec l'expression régulière `,.*`
3. Nettoyage de la colonne avec `\(.*` remplacé par rien pour supprimer les informations sur le pays de la ville
4. Nettoyage de la colonne avec `Paris.*` remplacé par "Paris" pour supprimer l'indication de la bibliothèque, déjà déplacée dans **Institution conservation item**



## Etape 4: la colonne Informations item

1. Création de la colonne **Informations item** grâce à a séparation des colonnes avec l'expression régulière `()\(.*` pour récupérer tout ce qui vient après la première parenthèse dans la colonne **Institution conservation item**. 
2.Nettoyage de la colonne **Institution conservation item** avec un *find and replace* `\(.*` par rien pour enlever les infos d'identification des items. 


Avec ces deux étapes, quelques informations comme la précision qu'une bibliothèque municipale est la bibliothèque `(Méjanes)` (information indiquée entre parenthèses dans la colonne **Institution conservation item**) sont moins bien placées mais ce sont des cas isolés et les informations d'identification des items sont trop diverses pour permettre de les trier sans risquer d'en perdre plus.



## Etape 5: les coordonnées

1. Nettoyage de la colonne **Institution conservation item**: faire un *find and replace* avec "Bibliothèque nationale de France. Département des manuscrits" remplacé par "Bibliothèque nationale de France"
2. Utiliser le script Python suivant:

```Python
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

    """
    # Pour tester le code sur une portion limitée des enregistrements
    if i > 15:
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
            nouveauSet[cle].append("")

    i +=1

    """
    # Pour tester le code sur une portion limitée des enregistrements
    if i > 15:
        break
    """

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
"""
print(resultats)
for attribut in nouveauSet:
    print(attribut + ": " + str(len(nouveauSet[attribut])))
"""

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Write recipe outputs
bp16_loc_enrich_df = pd.DataFrame(nouveauSet)
bp16_loc_enrich = dataiku.Dataset("bp16-loc-enrich")
bp16_loc_enrich.write_with_schema(bp16_loc_enrich_df)
```