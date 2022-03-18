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
1. Renommer la colonne **?localisation** en **Ville item**
2. Nettoyage des données: faire un *find and replace* avec l'expression régulière `,.*`
3. Nettoyage de la colonne avec `\(.*` remplacé par rien pour supprimer les informations sur le pays de la ville
4. Nettoyage de la colonne avec `Paris.*` remplacé par "Paris" pour supprimer l'indication de la bibliothèque, déjà déplacée dans **Institution conservation item**



## Etape 4: la colonne Informations item

1. Création de la colonne **Informations item** grâce à a séparation des colonnes avec l'expression régulière `()\(.*` pour récupérer tout ce qui vient après la première parenthèse dans la colonne **Institution conservation item**. 
2.Nettoyage de la colonne **Institution conservation item** avec un *find and replace* `\(.*` par rien pour enlever les infos d'identification des items. 


Avec ces deux étapes, quelques informations comme la précision qu'une bibliothèque municipale est la bibliothèque `(Méjanes)` (information indiquée entre parenthèses dans la colonne **Institution conservation item**) sont moins bien placées mais ce sont des cas isolés et les informations d'identification des items sont trop diverses pour permettre de les trier sans risquer d'en perdre plus.
