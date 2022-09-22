'''
This file takes as an input a post id from reddit and saves the tree as json to disk
'''
import json
import praw
from treelib import Tree

class RedditParser():

    def __init__(self, credentials):
        self.credentials = credentials
        with open(credentials) as f:
            creds = json.load(f)
            
        # create reddit instance
        self.reddit = praw.Reddit(client_id=creds['client_id'],
                            client_secret=creds['client_secret'],
                            user_agent=creds['user_agent'],
                            redirect_uri=creds['redirect_uri'],
                            refresh_token=creds['refresh_token'])


    def write_json_to_file(self, filename, json_str):
        folder = r"tree_data/"
        path_name = folder+filename
        with open(path_name,"w") as f:
            f.write(json.dumps(json_str))
        #tree.save2file(path_name+".txt")
        
        
    def create_tree(self, submission_id):
        submission = self.reddit.submission(submission_id)
        submission.comments.replace_more(limit=None)
        tree = Tree()
        # root node
        tree.create_node(str(submission.author), str(submission.id)) 
        # traverse the tree
        for comment in submission.comments.list():
            if comment.author == "AutoModerator":continue
            tree.create_node(
                str(comment.author),
                str(comment.id), 
                parent=str(comment.parent_id[3:]),
                data = {"body":comment.body, "score":comment.score}
            )
        return tree


    # extracts top submissions of a subreddit
    def extract_top_submissions(self, subreddit, limit):
        submission_ids = set()
        submissions = subreddit.hot(limit=limit)

        for sub in submissions:
            submission_ids.add(sub.id)
        
        return submission_ids
            
    # puts all trees in a json string
    def create_merged_json(self, subs):
        tree = self.create_tree(subs[0])
        json_str = json.loads(tree.to_json(with_data=True))
        for sub_id in subs[1:]:
            tree = self.create_tree(sub_id)
            tree_json = json.loads(tree.to_json(with_data=True))
            json_str.update(tree_json)
        
        return json_str
    

if __name__ == "__main__":
    #settings
    credentials = 'client_secrets.json'

    reddit_parser = RedditParser(credentials)

    reddit = reddit_parser.reddit
    # positive sub
    coronavirus_sub = reddit.subreddit("Coronavirus")
    # negative sub
    conspiracy_sub = reddit.subreddit("conspiracy")

    corona_subs = reddit_parser.extract_top_submissions(coronavirus_sub, 10)
    # ids = ["xkti8v", "xdn27t"]
    print(corona_subs)
    json_string = reddit_parser.create_merged_json(list(corona_subs))

    # tree = create_tree(reddit, submission_id)
    reddit_parser.write_json_to_file("coronavirus.json",json_string)