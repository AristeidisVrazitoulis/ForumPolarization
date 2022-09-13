import json
import praw
import pandas as pd

subr = 'pythonsandlot'
credentials = 'client_secrets.json'

with open(credentials) as f:
    creds = json.load(f)

reddit = praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     redirect_uri=creds['redirect_uri'],
                     refresh_token=creds['refresh_token'])

# subreddit = reddit.subreddit(subr)


print(reddit.user.me())
# title = 'Just Made My first Post on Reddit Using Python.'
# selftext = 'I am learning how to use the Reddit API with Python using the PRAW wrapper.'
 

# hot_posts = reddit.subreddit('all').hot(limit=10)
# for post in hot_posts:
#     print(post.title)

posts = []
ml_subreddit = reddit.subreddit('MachineLearning')
# for post in ml_subreddit.hot(limit=10):
#     posts.append([post.title, post.score, post.id, post.subreddit, post.num_comments, post.selftext, post.created])


# df = pd.DataFrame(posts,columns=['title', 'score', 'id', 'subreddit', 'num_comments', 'body', 'created'])
# print(df)

submission = reddit.submission(id="vg5kjd")
submission.comments.replace_more(limit=None)
# traverses all comments
for comment in submission.comments.list():
    print(comment.body)