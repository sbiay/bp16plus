with open("requetes/cerl-imprim-paris.text", mode="w") as f:
    r = "https://data.cerl.org/thesaurus/_search?query=(" \
        "imprimeur%20paris)%20AND%20type%3Acnp&size=100&mode=default&format=json&from="
    hits = 4557
    compteur = 1
    while compteur < hits:
        f.write(r + str(compteur) + "\n")
        compteur += 100