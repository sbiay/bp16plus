import requests
i = 0
# On initie une liste pour les futurs résultats
selection = {
    'id': [],
    'nom': [],
    'dates': [],
    'dataBNF': [],
    'adresse': [],
}
# On parse les données du dataset sous la forme d'une liste de dictionnaires
for my_row_as_dict in cerl_imprim_paris.iter_rows():
    if i > 5:
        break
    
   
    selection["id"].append(my_row_as_dict["id"])
    selection["nom"].append(my_row_as_dict["name_display_line"])
    print()
    # A partir de l'identifiant de la personne, on récupère sa notice complète au format Json
    r = requests.get(f"https://data.cerl.org/thesaurus/{my_row_as_dict['id']}?format=json")
    noticeJson = r.json()
    
    # On parse le contenu de ce Json
    # On récupère les dates de la personne sous leur forme française
    for dates in noticeJson["data"]["bioDates"]:
        # Pour s'assurer de ne pas ajouter deux dates, on pose comme condition que l'index courant
        # n'a pas encore reçu de date
        if len(selection["dates"]) < i+1:
            if dates["lang"] == "fre":
                selection["dates"].append(dates["text"])
          
    # On récupère le lien vers la notice DataBNF            
    for liens in noticeJson["data"]["extDataset"]:
        if len(selection["dataBNF"]) < i+1:
            if liens["searchTerm"][:18] == "http://data.bnf.fr":
                selection["dataBNF"].append(liens["searchTerm"])
                
    # On récupère l'adresse de l'imprimeur
    for lieu in noticeJson["data"]["place"]:
        if len(selection["adresse"]) < i+1:
            if lieu["part"][0]["name"] == "Paris":
                if len(lieu["part"]) > 1:
                    selection['adresse'].append(lieu["part"][1]["address"])

    # TRES IMPORTANT : s'il n'y a pas de résultat dans le contenu parsé, on ajoute un NULL
    # car la cohérence des données repose sur l'absence de vide 
    for cle in selection:
        if len(selection[cle]) == i:
            selection[cle].append("NULL")
    

    print("index " + str(i))
    print(selection)
    print("nb dates : " + str(len(selection["dates"])))
    print("nb noms : " + str(len(selection["nom"])))
    print("nb idBNF : " + str(len(selection["dataBNF"])))
    print("nb adresse : " + str(len(selection["adresse"])))
    
    i += 1
    