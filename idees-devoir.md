Idées pour le devoir de données
====
Plan :
1. Objectifs
2. Recrutement du corpus de départ
	1. La sélection des données
	2. La requête Sparql
	3. Données récoltées
3. Enrichissements possibles
	1. Nationalité des auteurs
	2. Langue des ouvrages
	3. Adresses bibliographiques
4. Nettoyage du jeu primaire
	1. Dates
5. Jeux de données complémentaires
	1. cerl-imprim-paris
		1. Caractéristiques générales
		2. Traitements
			1. Ciblage des résultats pertinents
			2. Récupération des données issues des notices
6. Mise en place du travail de groupe

***

# <span style="color : rgb(015, 005, 230, 0.8)">Objectifs</span>
L'idée générale serait de partir d'un jeu de données renseignant les éditions avec leurs exemplaires, leurs auteurs, leurs libraires (chaque édition possède donc des doublons lorsqu'elle a plusieurs auteurs, plusieurs libraires ou plusieurs exemplaires) afin de procéder à des enrichissements sur :
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

Intégré au projet sous le nom `bp16-export-primaire`.

# <span style="color : rgb(015, 005, 230, 0.8)">Nettoyage du jeu primaire</span>
## <span style="color : rgb(020, 080, 170, 0.8)">Dates</span>
Les dates ont été traitées à partir de la donnée brute renseignée sous l'attribut **date complète**. Le champ **date ISO** résulte de la transformation de ces données selon la norme ISO-8601 et validées par un *pattern* que nous avons implémenté : yyyy-mm-dd.

Cas particuliers :
- Lorsque la **date complète** contient une information issue d'une analyse (elle figure entre crochets), c'est cette dernière valeur qui a été retenu pour renseigner l'attribut **date ISO**.
- Lorsque la **date complète** décrit un intervalle, la limite basse a été renseignée selon le même format que **date ISO** sous l'attribut **date ISO jusqu'à**

# <span style="color : rgb(015, 005, 230, 0.8)">Enrichissements du jeu primaire</span>
## <span style="color : rgb(020, 080, 170, 0.8)">Langue des ouvrages</span>
Il s'agit de récupérer les langues des **expressions** dont BP16 contient les **manifestations**.

1. Récupérer l'URI DataBNF de l'expression à partir de son URI BP16

2. Requêter l'URI de l'expression au moyen d'une requête Sparql sur DataBNF afin de requêter la langue de cette expression :
    ```sparql
    SELECT DISTINCT ?langue
    WHERE {
    <http://data.bnf.fr/ark:/12148/cb418775742#about> <http://rdvocab.info/RDARelationshipsWEMI/expressionManifested> ?uriexpression.
    ?uriexpression <http://purl.org/dc/terms/language> ?langue.
    } LIMIT 1
    ```
    Le résultat est dans le jeu `bp16-langExp`.

3. Traduire les URI ISO des langues en donnée parlante : résultat dans le jeu `bp16-langNorm`.

## <span style="color : rgb(020, 080, 170, 0.8)">Adresses bibliographiques</span>
Source à mobiliser : CERL. Les notices du CERL les plus pertinentes sont de type `cnp` (Personnes) : plus riches en information, elles renseignent notamment le type d'activité.

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
- Nom complet : cerl-imprim-paris
- Définition : export de toutes les personnes de CERL répondant à "imprimeur" et "Paris" (4557) :

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
On récupère au moyen d'un script python, `compute_cerl-imprim-paris-enrich.py` les données intéressantes dans la notice de chaque imprimeur à partir de l'`id` de type `cnp` contenu dans le jeu précédent.

La récupération de chaque notice se fait par une requête de type `https://data.cerl.org/thesaurus/cnp01118364?format=json&pretty` tous les ark, qui peuvent être précédés soit d'une adresse data BNF soit d'une adresse catalogue BNF (donc ne prendre que la fin)

- Problème : chaque notice serait convertie en un tableau à 950 colonnes si elle était importée telle quelle dans Dataiku. On procède donc à un parsage des données au moyen du script pour ne récupérer que celles répondant à certains conditions restreintes.

Les données nécessaires sont contenues sous les clés :
- `id` : identifiant CERL ;
- `extDataset` : s'y trouvent les liens data-BNF indispensables pour joindre des données à notre jeu principal ;
- `place` : informations de localisation des activités des imprimeurs.

