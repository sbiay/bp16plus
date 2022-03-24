import csv
import urllib.parse
import requests
import json

"""
Ce script ouvre un fichier CSV contenant des noms de ville et d'institution conservant des ouvrages
réalise des requêtes sparql sur Wikidata pour récupérer leurs coordonnées de localisation
et écrit le résultat dans un nouveau fichier CSV.
"""

# On initie la liste qui recevra les données extraites du fichier-source
ancienSet = []

# On récupère les données du fichier source
with open("donnees/lieux_conservation_distinct_prepared.csv") as csvf:
    lecteur = csv.reader(csvf, delimiter='\t')
    
    # On parse les lignes du CSV pour récupérer chaque donnée et l'écrire dans une liste
    for index, (nomVille, nomInstitution, concat) in enumerate(lecteur):
        ancienSet.append({
            "index": index,
            "nomVille": nomVille,
            "nomInstitution": nomInstitution,
            "concat": concat,
        })

resultats = {}

with open("donnees/lieux_conservation_enrich-plus.csv", mode="w") as csvf:
    ecriveur = csv.writer(csvf, delimiter="\t", quotechar="|")
    
    for item in ancienSet:
        if item["index"] == 0:
            ecriveur.writerow(
                [
                    item["index"],
                    "Ville conservation",
                    "Institution conservation",
                    "Ville et instution",
                    "Coordonnees"
                ]
            )
        
        # On cherche le nom de la ville et de l'institution dans le journal des résultats
        elif resultats.get(item["concat"]):
            ecriveur.writerow(
                [item["index"], item["nomVille"], item["nomInstitution"], item["concat"], resultats[item["concat"]]]
            )
            print(f"Journal utilisé pour {item['concat']} : valeur {resultats[item['concat']]}")
        # Si le nom de la ville et de l'institution ne sont pas déjà dans le journal des résultats
        else:
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
                filter contains(?nomLieu, "''' + item["nomVille"] + '''")\n
                filter contains(lcase(?nomInstitution), "''' + item['nomInstitution'].lower() + '''").
                }\n
                LIMIT 1'''
            
            requHTTP = requests.get(
                "https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(queryString))
            
            if requHTTP.status_code == 200:
                try:
                    resultat = requHTTP.json()
                    # S'il y a un résultat
                    if len(resultat["results"]["bindings"]) >= 1:
                        donneeCoord = resultat["results"]["bindings"][0]["coordonnees"]["value"]
                        # On écrit le résultat dans le fichier de sortie
                        ecriveur.writerow(
                            [item["index"], item["nomVille"], item["nomInstitution"], item["concat"],
                            donneeCoord]
                        )
                        # On inscrit le résultat dans le journal des résultats
                        resultats[item["concat"]] = donneeCoord
                        print(item["concat"] + " : " +  donneeCoord)
        
                    else:
                        resultats[item["concat"]] = "NULL"
                        ecriveur.writerow(
                            [item["index"], item["nomVille"], item["nomInstitution"], item["concat"],
                            "NULL"]
                        )
    
                except json.decoder.JSONDecodeError:
                    print(f"There was a problem accessing the equipment data on {item['index']}.")