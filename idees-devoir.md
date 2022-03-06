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
4. Jeux de données complémentaires
5. Mise en place du travail de groupe

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

# <span style="color : rgb(015, 005, 230, 0.8)">Enrichissements possibles</span>
## <span style="color : rgb(020, 080, 170, 0.8)">Nationalité des auteurs</span>
Source de la donnée : Data-BNF.

Problèmes :
- Les auteurs de l'Antiquité comme Augustin n'ont pas de nationalité ; en revanche ils ont des dates, or tous les auteurs antérieurs à une date déterminée peuvent être considérés comme des auteurs antiques indépendamment de leur nationalité.

## <span style="color : rgb(020, 080, 170, 0.8)">Langue des ouvrages</span>
Généralement pas de lien vers des notices oeuvres Data-BNF =(

**Relancer la recherche**.

## <span style="color : rgb(020, 080, 170, 0.8)">Adresses bibliographiques</span>
Source à mobiliser : CERL. Les notices du CERL les plus pertinentes sont de type `cnp` (Personnes) : plus riches en information, elles renseignent notamment le type d'activité.

Les notices contiennent le référent ark de la BNF.

Les adresses bibliographiques sont associées à des années d'activité.

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
## cerl-imprim-paris

### Caractéristiques générales
- Nom complet : cerl-imprim-paris
- Définition : export de toutes les personnes de CERL répondant à "imprimeur" et "Paris" (4557) :

### Acquisition
- Méthode d'acquisition : liste des requêtes pour chaque 100 résultats dans `./requetes/cerl-imprim-paris.text`.
- Exemples de requête : 
    - https://data.cerl.org/thesaurus/_search?query=(imprimeur%20paris)%20AND%20type%3Acnp&size=100&mode=default&format=json&from=1
    - https://data.cerl.org/thesaurus/_search?query=(imprimeur%20paris)%20AND%20type%3Acnp&size=100&mode=default&format=json&from=101
    - https://data.cerl.org/thesaurus/_search?query=(imprimeur%20paris)%20AND%20type%3Acnp&size=100&mode=default&format=json&from=201

### Traitement
=> Prévoir un traitement python pour récupérer, à partir de chaque id de type cnp, via la requête de type `https://data.cerl.org/thesaurus/cnp01118364?format=json&pretty` tous les ark, qui peuvent être précédés soit d'une adresse data BNF soit d'une adresse catalogue BNF (donc ne prendre que la fin)

- Problème : ce fichier Json serait converti en 950 colonnes s'il était importé tel quel dans Dataiku. On procède donc à un parsage des données au moyen d'un script pour ne récupérer que celles répondant à certains conditions restreintes.

### Parsage
Les données nécessaires sont contenues sous les clés :
- `id` : identifiant CERL ;
- `extDataset` : s'y trouvent les liens data-BNF indispensables pour joindre des données à notre jeu principal ;
- `place` : informations de localisation des activités des imprimeurs.

Sélection des données :
- Sous la clé `extDataset` : on récupère la première valeur qui corresponde à une URI Data-BNF
- Sous la clé `place` :

# <span style="color : rgb(015, 005, 230, 0.8)">Mise en place du travail de groupe</span>
Nous avons besoin :
- D'un calendrier précisant les créneaux de travail à s'approprier ;
- D'un dépôt partagé pour le stockage de l'archive zip du projet ;
- D'un nom pour le projet :
    - bp16plus ?
- D'un plan de nommage ou de sauvegarde des archives zip.
- Un dépôt Github où chacun documente son travail dans une branche ? Permettrait aussi de rédiger la doc du devoir.

Reprendre les notes du framapad : https://annuel2.framapad.org/p/bp16pluspad-9svq?lang=fr