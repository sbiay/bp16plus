Mes requêtes sur Data-bnf
===

Serveur : https://data.bnf.fr/sparql

# Auteurs
1. La forme retenue et toutes les formes rejetés de la notice de saint Augustin:
    ```sparql
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT DISTINCT ?forme_retenue
    ?formes_rejetees 
    WHERE {<http://data.bnf.fr/ark:/12148/cb11889551s> skos:altLabel ?formes_rejetees;
    skos:prefLabel ?forme_retenue}
    ```

2. La forme retenue de *Quatre-vingt treize questions* :
    ```sparql
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?titre
    WHERE {
    <http://data.bnf.fr/ark:/12148/cb136202190> skos:prefLabel ?titre.
    }
    ```

3. **Personne** : tous les prédicats disponibles et tous les objets associés à saint Augustin :
    ```sparql
    SELECT DISTINCT ?p ?o
    WHERE {
    <http://data.bnf.fr/ark:/12148/cb11889551s#about> ?p ?o .
    }
    ```

4. Années de naissance et de mort d'Augustin :
    ```sparql
    PREFIX bnf-onto: <http://data.bnf.fr/ontology/bnf-onto/>
    SELECT DISTINCT ?naissance ?mort
    WHERE {
    <http://data.bnf.fr/ark:/12148/cb11889551s#about> bnf-onto:firstYear ?naissance .
    <http://data.bnf.fr/ark:/12148/cb11889551s#about> bnf-onto:lastYear ?mort .
    }
    ```

# Oeuvres
5. Tous les predicats et objets associés à *Quatre-vingt treize questions* :
    ```sparql
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?p ?o
    WHERE {
    <http://data.bnf.fr/ark:/12148/cb136202190#about> ?p ?o.
    }
    ```

6. Toutes les oeuvres dont Augustin est l'auteur:
    ```sparql
    PREFIX dcterms: <http://purl.org/dc/terms/>
    SELECT ?oeuvre
    WHERE {
    ?oeuvre dcterms:creator <http://data.bnf.fr/ark:/12148/cb11889551s#about>.
    }
    ```

7. L'URI dataBNF et l'URI BP16 d'après le nom d'un libraire : "Berthold Rembolt", avec tous ses prédicats :
    ```sparql
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    SELECT DISTINCT ?uri ?nom ?bp16 ?predicat ?objet
    WHERE {
      ?uri foaf:name "Berthold Rembolt".
      ?uri owl:sameAs ?bp16.
      ?uri ?predicat ?objet.
      FILTER REGEX (?bp16, "https://bp16").
    }
    ```

8. Toutes les **personnes** qui possèdent une notice **BP16** :

    ```sparql
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT DISTINCT ?uri ?bp16
    WHERE{
    ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> foaf:Person.
    ?uri owl:sameAs ?bp16.
    FILTER REGEX (?bp16, "https://bp16").
    }
    ```

9. Toutes les **manifestations** qui possèdent une notice BP16 (c'est au niveau des manifestations qu'il y a un lien BP16)
    ```SQL    
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT DISTINCT ?uri ?bp16
    WHERE{
      ?uri <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation>.
      ?uri <http://www.w3.org/2000/01/rdf-schema#seeAlso> ?bp16.
    }
    ```