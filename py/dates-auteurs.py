# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu
import urllib.parse
import requests
import json

# On charge le jeu de données de départ
bp16_export_primaire = dataiku.Dataset("bp16-datesNet")

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
            nouveauSet['nomAuteur'] = []
            nouveauSet['dateNaissance'] = []
            nouveauSet['dateMort'] = []

    # On récupère toutes les valeurs du jeu de départ pour les charger dans le nouveau jeu
    for attribut in enregistrement:
        nouveauSet[attribut].append(enregistrement[attribut])

    # On vérifie que l'enrichissement de la donnée n'ait pas déjà été fait
    # en cherchant l'idenfiant ark dans le journal des résultats
    ark = enregistrement['?auteur'][21:-13]
    if resultats.get(ark):
        # Si oui, on ajoute la donnée au nouveau set à partir du journal des résultats
        # CA NE VA PAS : avant on n'avait qu'une valeur dans le journal des résultats, maintenant il y en a trois
        nouveauSet['nomAuteur'].append(resultats[ark]["nom"])
        nouveauSet['dateNaissance'].append(resultats[ark]["naissance"])
        nouveauSet['dateMort'].append(resultats[ark]["mort"])
    else:
        # Comme il y a des oeuvres sans auteur, on pose comme condition l'existence de l'auteur
        if enregistrement['?auteur']:
            # On construit une URI DataBnF à partir du numéro ark contenu dans l'URI BP16 de la manifestation
            uriDataAuteur = f"http://data.bnf.fr/{ark}#about"

            # On écrit la requête Sparql
            # J'AI AJOUTE LE ?nomComplet, qui n'existe pas toujours mais est une info plus riche à privilégier
            queryString = '''SELECT DISTINCT ?nom ?nomComplet ?naissance ?mort
            WHERE {
            <''' + uriDataAuteur + '''> <http://xmlns.com/foaf/0.1/familyName> ?nom.
            <''' + uriDataAuteur + '''> <http://xmlns.com/foaf/0.1/name> ?nomComplet.
            <''' + uriDataAuteur + '''> <http://vocab.org/bio/0.1/birth> ?naissance.
            <''' + uriDataAuteur + '''> <http://vocab.org/bio/0.1/death> ?mort
            } LIMIT 1'''

            # On injecte la requête Sparql dans une requête HTTP grâce à la fonction urllib.parse.quote
            requHTTP = requests.get("https://data.bnf.fr/sparql?format=json&query=" + urllib.parse.quote(queryString))

            # Pour voir la tête du résultat de ta requête, cliques sur le lien imprimé par ceci
            if i == 162:
                print(f"https://data.bnf.fr/sparql?format=json&query=" + urllib.parse.quote(queryString))

            # On récupère le Json dans un try afin d'éviter les problèmes de décodage de fichier
            try:
                resultat = requHTTP.json()
                # On parse le résultat pour récupérer la valeur recherchée
                if len(resultat["results"]["bindings"])== 1:
                    # J'AI AJOUTE UNE CONDITION pour récupérer le nom complet s'il existe, sinon le nom de famille
                    if resultat["results"]["bindings"][0].get("nomComplet"):
                        donneeNom = resultat["results"]["bindings"][0]["nomComplet"]["value"]
                    else:
                        donneeNom = resultat["results"]["bindings"][0]["nom"]["value"]
                    donneeNaissance = resultat["results"]["bindings"][0]["naissance"]["value"]
                    donneeMort = resultat["results"]["bindings"][0]["mort"]["value"]

                # On remplit la valeur du nouvel attribut pour l'enregistrement courant
                nouveauSet['nomAuteur'].append(donneeNom)
                nouveauSet['dateNaissance'].append(donneeNaissance)
                nouveauSet['dateMort'].append(donneeMort)

                # LA ON A DU CHANGEMENT
                # On inscrit l'enrichissement dans le journal des résultats sous la forme d'un dictionnaire de dictionnaires
                resultats[ark] = {
                    "nom": donneeNom,
                    "naissance": donneeNaissance,
                    "mort": donneeMort
                }

            except json.decoder.JSONDecodeError:
                print(f"There was a problem accessing the equipment data on {enregistrement['?uriManif']}.")



    # TRES IMPORTANT : s'il n'y a pas de résultat dans le contenu parsé, on ajoute un NULL
    # car la cohérence des données repose sur l'absence de vide
    for cle in nouveauSet:
        if len(nouveauSet[cle]) == i:
            nouveauSet[cle].append("NULL")

    # On implémente l'index suivant
    i += 1

    """
    # Pour tester le code sur une portion limitée des enregistrements
    if i > 10000:
        break
    """

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# On imprime en test le nombre de valeur pour chaque attribut (il doit absolument être identique partout)
for attribut in nouveauSet:
    print(attribut + ": " + str(len(nouveauSet[attribut])))

print(resultats)

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# On implémente les résultats dans un objet DataFrame
bp16_nomAuteur_df = pd.DataFrame(nouveauSet)
bp16_dateNaissance_df = pd.DataFrame(nouveauSet)
bp16_dateMort_df = pd.DataFrame(nouveauSet)

# On écrit tout cela dans le dataset de sortie
bp16_nomAuteur = dataiku.Dataset("bp16-nomsAuteurs")
bp16_nomAuteur.write_with_schema(bp16_nomAuteur_df)
bp16_nomAuteur.write_with_schema(bp16_dateNaissance_df)
bp16_nomAuteur.write_with_schema(bp16_dateMort_df)