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
            f.write(json.dumps(json_str,indent=2))
        #tree.save2file(path_name+".txt")
        
        
    def create_tree(self, submission_id):
        submission = self.reddit.submission(submission_id)
        submission.comments.replace_more()
        tree = Tree()
        # root node
        tree.create_node(str(submission.author), str(submission.id)) 
        # traverse the tree
        for comment in submission.comments.list():
            #if comment.author == "AutoModerator":continue
            tree.create_node(
                str(comment.author),
                str(comment.id), 
                parent=str(comment.parent_id[3:]),
                data = {"body":comment.body, "score":comment.score}
            )
        return tree


    # extracts top submissions of a subreddit
    def extract_top_submissions(self, subreddit, limit):
        submission_ids = []
        submissions = subreddit.search("vaccine", limit=limit)
        for sub in submissions:
            submission_ids.append(sub.id)
        
        return submission_ids

    # takes a list of ids andd returns a set of trees (of comments) of treelib object
    def get_trees_by_id(self, ids):
        trees = set()
        for id in ids:
            trees.add(self.create_tree(id))
        return trees

            
    # puts all trees in a json string
    def create_merged_json(self, trees):
        json_obj = {}
        for tree in trees:
            json_tree = json.loads(tree.to_json(with_data=True))
            root_name = tree.get_node(tree.root).tag
            json_obj[root_name] = json_tree[root_name]

        return json_obj
    

if __name__ == "__main__":
    #settings
    credentials = 'client_secrets.json'

    reddit_parser = RedditParser(credentials)

    reddit = reddit_parser.reddit
    # positive sub
    coronavirus_sub = reddit.subreddit("Coronavirus")
    # negative sub
    conspiracy_sub = reddit.subreddit("conspiracy")


    corona_subs = reddit_parser.extract_top_submissions(coronavirus_sub, 5)
    conspiracy_subs = reddit_parser.extract_top_submissions(conspiracy_sub, 5)

    # ids = ["xkti8v", "xdn27t"]
    corona_trees = reddit_parser.get_trees_by_id(corona_subs)
    conspiracy_trees = reddit_parser.get_trees_by_id(conspiracy_subs)
    
    json_dict_corona = reddit_parser.create_merged_json(corona_trees)
    json_dict_conspiracy = reddit_parser.create_merged_json(conspiracy_trees)
    # #tree = create_tree(reddit, submission_id)
    reddit_parser.write_json_to_file("coronavirus.json", json_dict_corona)
    reddit_parser.write_json_to_file("conspiracy.json",json_dict_conspiracy)
