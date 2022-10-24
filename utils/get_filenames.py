


categories = ["top","controversial","both"]

def get_filenames_bysubreddit(subbreddit_name,ending):
    filenames = []
    for cat in categories:
        filenames.append(subbreddit_name+"_{}.{}".format(cat,ending))
    return filenames