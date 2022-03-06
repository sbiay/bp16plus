BP16 : modèle
===

# FRBR
BP16 ne contient que des **items** (qui renseignent les localisations) et des **manifestations** :
- http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation
- http://rdvocab.info/uri/schema/FRBRentitiesRDA/Item

## Manifestations
- Tous les prédicats et objets associés à une édition donnée :
    ```SQL
    SELECT DISTINCT ?p ?o
    WHERE { 
      <https://bp16.bnf.fr/ark:/12148/cb41874398s/> ?p ?o .
    }
    ```

## Items
- Tous les prédicats et objets associés à un item
    ```SQL
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT DISTINCT ?p ?o
    WHERE { 
      <https://bp16.bnf.fr/ark:/12148/cb41877504w/#item> ?p ?o .
    }
    ```

- Une manifestation et ses items :
  - Les items sont liés à la manif. par le prédicat http://rdvocab.info/RDARelationshipsWEMI/manifestationExemplified, dont l'objet est l'URI de la manif.

# Rôles
## Auteurs
- Une manifestation a pour auteur une personne :
    
    `?uri <http://data.bnf.fr/vocabulary/roles/r70> <https://data.bnf.fr/ark:/12148/cb13485815c#foaf:Person>`

## Imprimeurs libraires
- Une manifestation a pour imprimeur-libraire une personne :
    
    `?uri <http://data.bnf.fr/vocabulary/roles/r3260> <https://data.bnf.fr/ark:/12148/cb13516720n#foaf:Person>`

- Tous les imprimeurs-libraires :
    
    ```SQL
    SELECT DISTINCT ?o 
    WHERE { 
      ?s <http://data.bnf.fr/vocabulary/roles/r3260> ?o .
    } 
    ```

- Une manifestation a pour libraire (bookseler) une personne :

    `?uri <https://id.loc.gov/vocabulary/relators/bsl.html> <https://data.bnf.fr/ark:/12148/cb13516720n#foaf:Person>`


# De BP16 vers DataBnF
- Tous les prédicats d'une personne à partir de son URI de BP16 :

    ```saprql
    SELECT DISTINCT ?p ?o
    WHERE {
      ?uri ?p ?o.
      ?uri <http://www.w3.org/2002/07/owl#sameAs> <http://data.bnf.fr/ark:/12148/cb13485815c#foaf:Person>
    }
    ```