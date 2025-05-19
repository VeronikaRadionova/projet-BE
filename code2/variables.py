import pandas as pd
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
      
def getMergedDemandeDaide(dataframes):
    tweets = dataframes["Tweet_date_clean"]
    is_about = dataframes["is_about_clean"]
    events = dataframes["Event_clean"]
    help_requests = dataframes["help_requests"]

    # --- Normalisation ---
    tweets['tweet_id'] = tweets['tweet_id'].astype(str)
    is_about['tweet_id'] = is_about['tweet_id'].astype(str)
    help_requests['tweet_id'] = help_requests['tweet_id'].astype(str)
    events['event_id'] = events['event_id'].astype(str)
    is_about['event_id'] = is_about['event_id'].astype(str)

    # --- Corriger les event_id numériques ---
    event_id_map = dict(zip(events.index.astype(str), events['event_id']))
    is_about['event_id'] = is_about['event_id'].map(event_id_map)

    # --- Fusion ---
    merged = tweets.merge(is_about, on="tweet_id", how="inner")
    merged = merged.merge(events[['event_id', 'event_type']], on="event_id", how="left")
    merged = merged.merge(help_requests[['tweet_id', 'category_name']], on="tweet_id", how="left")
    merged['created_at'] = pd.to_datetime(merged['created_at'], errors='coerce')
    merged['is_help'] = merged['category_name'].notna()
    return merged