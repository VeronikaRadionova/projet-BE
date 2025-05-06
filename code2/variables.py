#TODO tous les lectures de CSV qui ont besoin d'etre fait une fois

def getCategories(dataframes):
    return dataframes["Event_clean"]["event_type"].dropna().unique()

def getCrises(dataframes):
    return dataframes["Event_clean"]["event_id"].dropna().unique()

def getDicoCrises(dataframes):
    return 1

      
