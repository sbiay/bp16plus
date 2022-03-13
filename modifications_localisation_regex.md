# Regex devoir données, modifs Zoé:

La colonne *?localisation* contient, en une seule fois, des informations concernant la *ville* et l'*institution* où sont conservés les ouvrages, ainsi que leur *cote* et leur *état*.

Pour chaque information, une nouvelle colonne est créée et les données sont déplacées de la colonnes principale vers la colonne adaptée.



## Etape 1: la colonne ?etat

1. D'abord, extraire les données avec le *extract with regular expression* et les importer dans une nouvelle colonne **?etat** en utilisant cette regex: `(\(?état.*\)?)`
2. Puis retirer ces données de la colonne **?localisation** avec la même regex.
3. Nettoyer les données de la colonne **?etat** en retirant les parenthèses avec un *find and replace*
4. Renommer la colonne en **?etat** au lieu du **?etat1** automatique


## Etape 2.1: la colonne ?institutionConservation

1. Depuis la colonne **?localisation**, même extraction des données avec cette expression régulière: `[,|.] (.*)$` vers la nouvelle colonne **?institutionConservation**
2. Nettoyage des chaînes de caractères: utiliser la regex: `(.*\), )` à ne remplacer par rien dans la colonne **?institutionConservation**





## Etape 3: la colonne ?villeConservation

1. Depuis la colonne **?localisation**, même extraction des données avec cette expression régulière: `^(.*)[,|(. )]` vers la nouvelle colonne **?villeConservation**
2. Nettoyage des données: faire un *find and replace* avec l'expression régulière `,.*`
3. Renommer la colonne sans le 1 automatique





! une valeur manquante dans institutionConservation, la retrouver?
! ajouter les parenthèses manquantes dans les villeConservation
! suppression de la colonne localisation




(## Etape 2.2: la colonne cote

1. Depuis la colonne **?institutionConservation**, même extraction des données avec cette expression régulière: `f` vers la nouvelle colonne **cote**

`(\((.*[0-9*])\)$)` xsl:non


II - **cote** : même procédé, avec l'expression régulière `(\(.*\))$`)