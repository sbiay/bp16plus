Idées pour le devoir de données
====
Plan :
1. Objectifs
2. Recrutement du corpus de départ
	1. La sélection des données
	2. La requête Sparql
	3. Données récoltées
3. Nettoyage du jeu primaire
	1. Dates
4. Enrichissements du jeu primaire
	1. Langue des ouvrages
	2. Adresses bibliographiques
5. Jeux de données complémentaires
	1. cerl-imprim-paris
		1. Caractéristiques générales
		2. Traitements
			1. Ciblage des résultats pertinents
			2. Récupération des données issues des notices
			3. Nettoyage des données relatives aux adresses bibliographiques
	2. wikidata-rues-paris
		1. Méthode d'acquisition détaillée

***

# <span style="color : rgb(015, 005, 230, 0.8)">Objectifs</span>
L'idée générale est de partir d'un jeu de données renseignant les éditions avec leurs exemplaires, leurs auteurs, leurs libraires (chaque édition possède donc des doublons lorsqu'elle a plusieurs auteurs, plusieurs libraires ou plusieurs exemplaires) afin de procéder à des enrichissements sur :
1. Les exemplaires : enrichir leur localisation (actuellement une chaîne de caractères) ;
2. Les auteurs ou les éditeurs, qui ne sont renseignés dans BP16 que sous forme de données liées de DataBNF ; il s'agirait donc de rapatrier des données explicites (noms, dates, lieu de naissance par exemple) ;
3. Les imprimeurs-libraires (idem).

# <span style="color : rgb(015, 005, 230, 0.8)">Recrutement du corpus de départ</span>
## <span style="color : rgb(020, 080, 170, 0.8)">La sélection des données</span>
On part des résultats d'une requête Sparql sur le jeu BP16. Les attributs recherchés sont :
- `?uriManif` : l'URI de chaque édition ("manifestation" en modèle FRBF) 
- `?identifiantBP16` : l'identifiant de chaque notice d'édition
- `?titre` : le titre de l'édition
- `?auteur` : le lien vers la notice Data-BNF d'un éventuel auteur 
- `?editeur` : le lien vers la notice Data-BNF d'un éventuel éditeur (éditeur du texte)
- `?lieuPublication` : le lieu de publication (toujours Paris en principe, mais je voulais vérifier)
- `?publisher` : le label sous lequel l'édition est publiée (imprimeur-libraire)
- `?date` : la date de publication
- `?imprLibraire` : le lien vers la notice Data-BNF d'un imprimeur-libraire
- `?catalogueBNF` : le lien vers la notice du catalogue de la BNF de l'édition
- `?uriItem` : l'URI de chaque examplaire d'une édition ("item" en modèle FRBF) 
- `?localisation` : le lieu de conservation de l'exemplaire

## <span style="color : rgb(020, 080, 170, 0.8)">La requête Sparql</span>
```SQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns2: <http://rdvocab.info/RDARelationshipsWEMI/>
PREFIX ns3: <http://rdvocab.info/roles/>
PREFIX ns1: <http://data.bnf.fr/ontology/bnf-onto/>
PREFIX ns6: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ns4: <http://RDVocab.info/Elements/>
PREFIX ns5: <http://data.bnf.fr/vocabulary/roles/>
SELECT DISTINCT ?uriManif ?identifiantBP16 ?titre ?auteur ?editeur ?lieuPublication ?publisher ?date ?imprLibraire ?catalogueBNF ?uriItem ?localisation
WHERE { 
  ?uriManif ns1:identifiantBP16 ?identifiantBP16. 
  ?uriManif ns6:title ?titre.
  ?uriManif rdfs:seeAlso ?catalogueBNF.
  ?uriManif ns4:dateOfPublication ?date.
  ?uriManif ns4:placeOfPublication ?lieuPublication.
  ?uriManif ns5:r3260 ?imprLibraire.
  ?uriItem ns2:manifestationExemplified ?uriManif.
  ?uriItem ns3:currentOwnerItem ?localisation.
  OPTIONAL {
      ?uriManif ns5:r70 ?auteur.
      ?uriManif ns5:r360 ?editeur.
      ?uriManif ns4:publishersName ?publisher.
    }
}
```

## <span style="color : rgb(020, 080, 170, 0.8)">Données récoltées</span>
Le résultat de la requête précédente est contenu dans le fichier `./donnees/bp16-manifestation-items-1.csv`.

Il est intégré au projet sous le nom `bp16-export-primaire`.

# <span style="color : rgb(015, 005, 230, 0.8)">Nettoyage du jeu primaire</span>
## <span style="color : rgb(020, 080, 170, 0.8)">Dates</span>
Les dates ont été traitées à partir de la donnée brute renseignée sous l'attribut **date complète**. Le champ **date ISO** résulte de la transformation de ces données selon la norme ISO-8601 et validées par un *pattern* que nous avons implémenté : yyyy-mm-dd.

Cas particuliers :
- Lorsque la **date complète** contient une information issue d'une analyse (elle figure entre crochets), c'est cette dernière valeur qui a été retenu pour renseigner l'attribut **date ISO**.
- Lorsque la **date complète** décrit un intervalle, la limite basse a été renseignée selon le même format que **date ISO** sous l'attribut **date ISO jusqu'à**

# <span style="color : rgb(015, 005, 230, 0.8)">Enrichissements du jeu primaire</span>
## <span style="color : rgb(020, 080, 170, 0.8)">Langue des ouvrages</span>
On a récupéré les langues des **expressions** dont BP16 contient les **manifestations**.

1. On a d'abord récupéré l'URI DataBNF de l'expression à partir de son URI BP16

2. Puis requêté l'URI de l'expression au moyen d'une requête Sparql sur DataBNF afin de requêter la langue de cette expression :
    ```sparql
    SELECT DISTINCT ?langue
    WHERE {
    <http://data.bnf.fr/ark:/12148/cb418775742#about> <http://rdvocab.info/RDARelationshipsWEMI/expressionManifested> ?uriexpression.
    ?uriexpression <http://purl.org/dc/terms/language> ?langue.
    } LIMIT 1
    ```
    Le résultat est dans le jeu `bp16-langExp`.

3. Traduit enfin les URI ISO des langues en donnée parlante : résultat dans le jeu `bp16-langNorm`.

## <span style="color : rgb(020, 080, 170, 0.8)">Adresses bibliographiques</span>

Les notices contiennent le référent ark de la BNF.

Méthode :
1. Parser le fichier Json :
    - Les adresses bibliographiques sont situées dans ["rows"][index de liste des personnes]["data"]["place"][0]["part"][index de liste]["address"]
    - Il s'agit d'un texte
    - Identifier la bonne adresse :
        - S'il y a plusieurs clés `address` dans la liste, le texte contient généralement deux dates entre `[]`, souvent après un seul `[`
        - Récupérer les dates et les comparer à la date de l'édition (selon une méthode "pas avant" ET "pas après").
    - Extraire les noms de rues :
        - Voir le projet "Odonyms" (onglet Firefox) peut servir
        - parser le texte et prendre tous les mots après "rue" et avant un signe de ponctuation.
2. Etablir le lien entre lieu et référentiel :
    1. Requêter le nom de la rue sur Wikidata : **à écarter car ne possède pas de réservoir de formes anciennes**
        - Dans Wikidata il faut joindre les *part of* (Property:P361)
            - wd:Q107311481, mais seulement 71 résultats
            - Il y a aussi la propriété street wd:Q79007 mais pas facile à croiser avec la données Paris
        - Lien vers les notices Wikipédia
            - Leur URL renvoie à un visualiseur de la position géographique : https://fr.wikipedia.org/wiki/Rue_de_l%27Arche-P%C3%A9pin#/maplink/0
            - coordinate location
    2. Croiser avec les données de `denominations-emprises-voies-actuelles.json` (données de Paris Data) :
        - Développer le script `voirie.py`


# <span style="color : rgb(015, 005, 230, 0.8)">Jeux de données complémentaires</span>
## <span style="color : rgb(020, 080, 170, 0.8)">cerl-imprim-paris</span>
### <span style="color : rgb(000, 200, 100, 0.7)">Caractéristiques générales</span>
- Source mobilisée : [CERL Thesaurus](https://data.cerl.org/thesaurus/_search).
- Nom du jeu : `cerl-imprim-paris`
- Définition : export de toutes les **personnes** de CERL répondant à "imprimeur" et "Paris" (4557). Les notices du CERL les plus pertinentes sont en effet de type `cnp` ("personnes") : plus riches en information, elles renseignent notamment le type d'activité.
- Méthode d'acquisition : liste des requêtes pour chaque 100 résultats dans `./requetes/cerl-imprim-paris.text`. 
- Exemples de requête : 
    - https://data.cerl.org/thesaurus/_search?query=(imprimeur%20paris)%20AND%20type%3Acnp&size=100&mode=default&format=json&from=1
    - https://data.cerl.org/thesaurus/_search?query=(imprimeur%20paris)%20AND%20type%3Acnp&size=100&mode=default&format=json&from=101
    - https://data.cerl.org/thesaurus/_search?query=(imprimeur%20paris)%20AND%20type%3Acnp&size=100&mode=default&format=json&from=201

### <span style="color : rgb(000, 200, 100, 0.7)">Traitements</span>
#### <span style="color : rgb(050, 100, 060, 0.7)">Ciblage des résultats pertinents</span>
On élimine la majorité des lignes non pertinentes en appliquant un *filter* sur l'attribut `additional_display_line`, *contains* 15 : ce champ commence par les dates ; poser que le champ contient 15 élimine de nombreux imprimeur qui n'ont pas 15 dans leur date de naissance ou de mort.

On obtient le set `cerl-imprim-paris_filtered` (env. 1000 lignes au lieu de 4500).

#### <span style="color : rgb(050, 100, 060, 0.7)">Récupération des données issues des notices</span>
On récupère au moyen d'un script python (`compute_cerl-imprim-paris-enrich.py`) les données intéressantes dans la notice de chaque imprimeur à partir de l'`id` de type `cnp` contenu dans le jeu précédent.

La récupération de chaque notice se fait par une requête de type `https://data.cerl.org/thesaurus/cnp01118364?format=json&pretty`. On parse le contenu de chaque Json pour récupérer le numéro ark (qui peut être précédé soit d'une adresse data.bnf.fr soit d'une adresse catalogue.bnf.fr.

Chaque notice peut comporter jusqu'à 950 attributs. On procède donc à un parsage des données au moyen du script pour ne récupérer que celles répondant à certains conditions restreintes.

Les données nécessaires sont contenues sous les clés :
- `id` : identifiant CERL ;
- `extDataset` : s'y trouvent les liens vers les ressources de la BNF contenant les numéros ark indispensables pour joindre les données à notre jeu principal ;
- `place` : informations de localisation des activités des imprimeurs.

On obtient le jeu `cerl-imprim-paris-enrich`.

#### <span style="color : rgb(050, 100, 060, 0.7)">Nettoyage des données relatives aux adresses bibliographiques</span>
A partir du jeu obtenu, on effectue un ensemble de traitements à base d'expressions régulières, pour générer une colonne "adresse simplifiée".

On obtient le jeu `cerl-imprim-paris-rues`.

## <span style="color : rgb(020, 080, 170, 0.8)">wikidata-rues-paris</span>
- Source mobilisée : Wikidata.
- Nom du jeu : `wikidata-rues-paris`
- Définition : export de données liées répondant à la description `"street in Paris, France"@en`, plus riche que son homologue francophone.
- Méthode d'acquisition : on récupère de Wikidata une liste des noms des rues de Paris avec leurs coordonnées en passant deux requêtes HTTP successives exprimant deux requêtes Sparql.

### Jeu de données concurrent écarté
Nous avons examiné le jeu de données [Dénominations des emprises des voies actuelles](https://opendata.paris.fr/explore/dataset/denominations-emprises-voies-actuelles/export/?disjunctive.siecle&disjunctive.statut&disjunctive.typvoie&disjunctive.arrdt&disjunctive.quartier&disjunctive.feuille&sort=historique) disponible sur opendata.paris.fr.

Les informations relatives aux anciens noms de rues y sont contenues dans un champ "historique" touffu dont il n'a pas été possible d'extraire de façon satisfaisante les seuls noms des rues.

### Méthode d'acquisition détaillée
1. Avec le nom principal de l'entité :
    ```sparql
    SELECT ?entite ?nom ?coordonnees
    WHERE {
        ?entite schema:description "street in Paris, France"@en.
        ?entite rdfs:label ?nom.
        ?entite p:P625 ?proprieteLoc.
        ?proprieteLoc ps:P625 ?coordonnees.
    }
    ```
2. Avec les noms autres :
    ```sparql
    SELECT ?entite ?nom ?coordonnees
    WHERE {
        ?entite schema:description "street in Paris, France"@en.
        ?entite skos:altLabel ?nom.
        ?entite p:P625 ?proprieteLoc.
        ?proprieteLoc ps:P625 ?coordonnees.
    }
    ```
Requêtes HTTP :
- https://query.wikidata.org/sparql?format=json&query=SELECT%20%3Fentite%20%3Fnom%20%3Fcoordonnees%0A%20%20%20%20WHERE%20%7B%0A%20%20%20%20%20%20%20%20%3Fentite%20schema%3Adescription%20%22street%20in%20Paris%2C%20France%22%40en.%0A%20%20%20%20%20%20%20%20%3Fentite%20rdfs%3Alabel%20%3Fnom.%0A%20%20%20%20%20%20%20%20%3Fentite%20p%3AP625%20%3FproprieteLoc.%0A%20%20%20%20%20%20%20%20%3FproprieteLoc%20ps%3AP625%20%3Fcoordonnees.%0A%20%20%20%20%7D
- https://query.wikidata.org/sparql?format=json&query=SELECT%20%3Fentite%20%3Fnom%20%3Fcoordonnees%0A%20%20%20%20WHERE%20%7B%0A%20%20%20%20%20%20%20%20%3Fentite%20schema%3Adescription%20%22street%20in%20Paris%2C%20France%22%40en.%0A%20%20%20%20%20%20%20%20%3Fentite%20skos%3AaltLabel%20%3Fnom.%0A%20%20%20%20%20%20%20%20%3Fentite%20p%3AP625%20%3FproprieteLoc.%0A%20%20%20%20%20%20%20%20%3FproprieteLoc%20ps%3AP625%20%3Fcoordonnees.%0A%20%20%20%20%7D

Puis on nettoie les valeurs avec une recette d'expression régulières et on ne garde que les labels français.

### Bilan de la réunion avec le jeu de données principal
De nombreuses adresses bibliographiques n'ont pas trouvé de correspondance suite à la jointure de ces données avec celles issues du CERL. Mais il était intéressant d'effectuer cet enrichissement, bien que la complétude des données soit limitée.