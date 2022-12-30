

all_subreddits = ["Coronavirus","conspiracy","science", "WitchesVsPatriarchy", "MensRights", "lgbt", "Conservative", "conspiracy0", "space"]

topics = {
    "covid": ["Coronavirus","conspiracy","science","worldnews"],
    "patriarchy": ["WitchesVsPatriarchy","MensRights"]
}

categories = ["top","controversial","both"]

def get_filenames_by_subreddit(subbreddit_name, ending="", modified=False):
    filenames = []
    for cat in categories:
        
        filename = f"{subbreddit_name}_{cat}"
        
        if modified: filename += "_modified"
        if ending != "": filename += f".{ending}"

        filenames.append(filename)
    return filenames