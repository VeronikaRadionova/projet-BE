#TODO tous les lectures de CSV qui ont besoin d'etre fait une fois

def getCategories(dataframes):
    return list(dataframes["Event_clean"]["event_type"].dropna().unique())

def getCrises(dataframes):
    return list(dataframes["Event_clean"]["event_id"].dropna().unique())

def getTrecisCrises(dataframes):
    crises=getCrises(dataframes)
    trecis=list(dataframes["Event_clean"]["trecis_id"].dropna().unique())
    dico={}
    for i in range (len(crises)):
        dico[trecis[i]]=crises[i]
    return dico

def getCrisesTrecis(dataframes):
    crises=getCrises(dataframes)
    trecis=list(dataframes["Event_clean"]["trecis_id"].dropna().unique())
    dico={}
    for i in range (len(crises)):
        dico[crises[i]]=trecis[i]
    return dico
      
