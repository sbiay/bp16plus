# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# -*- coding: utf-8 -*-
import requests
import json
import dataiku
import pandas as pd, numpy as np
from dataiku import pandasutils as pdu

# On importe le jeu de données à traiter
cerl_imprim_paris = dataiku.Dataset("cerl-imprim-paris_filtered")

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# On initie l'index des lignes que l'on va traiter
i = 0
# On initie le dataFrame pour les futures données parsées
selection = {
    'id': [],
    'nom': [],
    'dates': [],
    'dataBNF': [],
    'adresseParis': [],
}

# On ouvre un fichier de rapport d'erreur pour les problèmes de lecture de Json
with open("/home/sbiay/chantiers/bp16plus/rapports/compute_cerl-imprim-paris-enrich-Json.txt", mode="w") as rapportJson:

    # On parse les données du dataset sous la forme d'une liste de dictionnaires
    for my_row_as_dict in cerl_imprim_paris.iter_rows():
        # On récupère l'id
        # Pour s'assurer de ne pas ajouter deux dates, on pose comme condition que l'index courant
        # n'a pas encore reçu de date
        if len(selection["id"]) < i+1:
            selection["id"].append(my_row_as_dict["id"])

        # On récupère le nom de la personne
        if len(selection["nom"]) < i+1:
            selection["nom"].append(my_row_as_dict["name_display_line"])

        # A partir de l'identifiant de la personne, on récupère sa notice complète au format Json
        r = requests.get(f"https://data.cerl.org/thesaurus/{my_row_as_dict['id']}?format=json")

        # On récupère le Json dans un try afin d'éviter les problèmes de décodage de fichier
        try:
            noticeJson = r.json()

            # On parse le contenu de ce Json
            # On récupère les dates au format français
            if len(selection["dates"]) < i+1:
                if noticeJson["data"].get("bioDates"):
                    for dates in noticeJson["data"]["bioDates"]:

                        if dates["lang"] == "fre":
                            selection["dates"].append(dates["text"])
            # On récupère le lien vers la notice DataBNF
            if len(selection["dataBNF"]) < i+1:
                if noticeJson["data"].get("extDataset"):
                    for liens in noticeJson["data"]["extDataset"]:
                        if liens["searchTerm"][:18] == "http://data.bnf.fr":
                            selection["dataBNF"].append(liens["searchTerm"] + "#about")
            # Faute d'un identifiant dataBNF, on le reconstruit en récupérant l'ark
            # s'il existe un lien vers une notice du CG BNF
            if len(selection["dataBNF"]) < i+1:
                if noticeJson["data"].get("extDataset"):
                    for liens in noticeJson["data"]["extDataset"]:
                        if liens["searchTerm"][:18] == "http://catalogue.bn":
                            selection["dataBNF"].append("http://data.bnf.fr" + liens["searchTerm"][23:] + "#about")

            # On récupère l'adresse de l'imprimeur
            if len(selection["adresseParis"]) < i+1:
                if noticeJson["data"].get("place"):
                    for lieu in noticeJson["data"]["place"]:
                        if lieu["part"][0]["name"] == "Paris":
                            if len(lieu["part"]) > 1:
                                if lieu["part"][1].get("address"):
                                    selection['adresseParis'].append(lieu["part"][1]["address"])
            # TRES IMPORTANT : s'il n'y a pas de résultat dans le contenu parsé, on ajoute un NULL
            # car la cohérence des données repose sur l'absence de vide
            for cle in selection:
                if len(selection[cle]) == i:
                    selection[cle].append("NULL")
            # On implémente l'index suivant
            i += 1

        except json.decoder.JSONDecodeError:
            rapportJson.write(f"There was a problem accessing the equipment data on {my_row_as_dict['id']}.")

# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# On implémente les résultats dans un objet DataFrame
cerl_imprim_paris_enrich_df = pd.DataFrame(selection)


# On écrit tout cela dans le dataset de sortie
cerl_imprim_paris_enrich = dataiku.Dataset("cerl-imprim-paris-enrich")
cerl_imprim_paris_enrich.write_with_schema(cerl_imprim_paris_enrich_df)