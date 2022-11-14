import praw
import json

#settings

def get_reddit_instance():
    credentials = 'client_secrets.json'

    with open(credentials) as f:
                creds = json.load(f)
                
            # create reddit instance
    reddit = praw.Reddit(client_id=creds['client_id'],
                        client_secret=creds['client_secret'],
                        user_agent=creds['user_agent'],
                        redirect_uri=creds['redirect_uri'],
                        refresh_token=creds['refresh_token'])
    return reddit




