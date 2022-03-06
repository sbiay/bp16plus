Comment faire le pont entre bp16 et CERL Thesaurus ?
====

# Wikidata
Point d'entrée Wikidata : https://query.wikidata.org/

Exemple de Berthold Rembolt :
Son URI wikidata : http://www.wikidata.org/entity/Q30593480

**Prédicats**   **URI**
rdfs:label	    Berthold Rembolt
wdtn:P268	      <http://data.bnf.fr/ark:/12148/cb13516720n#about>
wdtn:P1871	    <http://thesaurus.cerl.org/record/cni00040058>

[Préfixes wikidata](https://www.wikidata.org/wiki/EntitySchema:E49) :
- PREFIX wdtn: <http://www.wikidata.org/prop/direct-normalized/>
- PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

Documentation complémentaire : [comment faire des requêtes wikidata](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/queries/examples) ?

## Requête à partir d'un ark DataBNF pour obtenir un identifiant CERL
On applique une limite de 2 car les tests ont permis de constater que dans ce cas, les résultats sont redondants à partir du troisième :
```sparql
PREFIX wdtn: <http://www.wikidata.org/prop/direct-normalized/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?uri ?nom ?idcerl
WHERE {
  ?uri wdtn:P268 <http://data.bnf.fr/ark:/12148/cb13516720n#about>.
  ?uri rdfs:label ?nom.
  ?uri wdtn:P1871 ?idcerl.
} LIMIT 2
```

## Implémenter la requête en python
Pour récupérer le contenu de la requête
```py
import requests
import json

url = 'https://query.wikidata.org/sparql'
query = '''
PREFIX wdtn: <http://www.wikidata.org/prop/direct-normalized/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?uri ?nom ?idcerl
WHERE {
  ?uri wdtn:P268 <http://data.bnf.fr/ark:/12148/cb13516720n#about>.
  ?uri rdfs:label ?nom.
  ?uri wdtn:P1871 ?idcerl.
} LIMIT 2
'''
r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()
with open("/home/sbiay/chantiers/bp16/test.json", mode="w") as f:
    json.dump(data, f)
```
A partir de là, on peut créer une fonction de requêtage des id. CERL à partir des ark =)

# Astuces : requêtes sur CERL
- Rechercher toutes les personnes de la base : `https://data.cerl.org/thesaurus/_search?query=(*) AND type:cnp`

# De Wikidata vers CERL
1. Toutes les URI ayant un idCERL ET un identifiant BNF, avec le nom et les dates des personnes :
  ```sparql
  PREFIX wd: <http://www.wikidata.org/entity/>
  PREFIX wdtn: <http://www.wikidata.org/prop/direct-normalized/>
  SELECT ?nom ?uri ?idcerl ?idBNF ?naissance ?mort
  WHERE {
  ?uri wdtn:P1871 ?idcerl.
  ?uri wdtn:P268 ?idBNF.
  ?uri wdt:P569 ?naissance.
  ?uri wdt:P570 ?mort.
  ?uri wdt:P1559 ?nom
}

Ne donne pas les résultats attendus ! Les correspondances entre CERL et Wikidata sont trop ténues