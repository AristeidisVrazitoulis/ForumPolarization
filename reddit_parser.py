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

        
        self.delete_ids = set()


    def write_json_to_file(self, filename, json_str):
        folder = r"tree_data/"
        path_name = folder+filename
        with open(path_name,"w") as f:
            f.write(json.dumps(json_str,indent=2))
        
        
    def create_tree(self, submission_id):
        submission = self.reddit.submission(submission_id)
        submission.comments.replace_more()
        tree = Tree()
        # root node
        tree.create_node(str(submission.author), str(submission.id), data={"score":submission.score,"body":submission.selftext}) 
        # traverse the tree
        for comment in submission.comments.list():
            comment_author = str(comment.author)
            author_name = comment_author+str(comment.id) if comment_author == "None" else comment_author

            tree.create_node(
                author_name,
                str(comment.id), 
                parent=str(comment.parent_id[3:]),
                data = {"body":comment.body, "score":comment.score}
            )
        return tree


    # extracts top submissions of a subreddit
    def extract_top_submissions(self, subreddit, limit):
        submission_ids = []
        submissions = subreddit.search("vaccin", limit=None)
        print(len(list(submissions)))
        for sub in submissions:
            submission_ids.append(sub.id)
        
        return submission_ids


    # extracts top submissions of a subreddit
    def extract_controversial_submissions(self, subreddit, limit):
        submission_ids = []
        submissions = subreddit.controversial(time_filter="all", limit = None)
       
        counter = 0
        for sub in submissions:
            if "vaccin" in sub.selftext or "vaccin" in sub.title:
                #print(sub.selftext)
                submission_ids.append(sub.id)
                counter += 1
                # if counter == limit:
                #     break
        return submission_ids

    # takes a list of ids andd returns a set of trees (of comments) of treelib object
    def get_trees_by_id(self, ids):
        trees = set()
        for id in ids:
            trees.add(self.create_tree(id))
        return trees

            
    # puts all trees in a dictionary
    def create_merged_json(self, trees):
        json_obj = {}
        for tree in trees:
            json_tree = json.loads(tree.to_json(with_data=True))
            root_name = tree.get_node(tree.root).tag
            json_obj[root_name] = json_tree[root_name]

        return json_obj

    def get_json_trees_by_subreddit(self, subreddit_name, limit):
        sub = self.reddit.subreddit(subreddit_name)
        # controversial_subs = self.extract_controversial_submissions(sub, limit)
        relevant_subs = self.extract_top_submissions(sub, limit)
        trees = self.get_trees_by_id(relevant_subs)
        json_dict = self.create_merged_json(trees)
        return json_dict

    

if __name__ == "__main__":
    #settings
    credentials = 'client_secrets.json'
    save_to_file = False


    reddit_parser = RedditParser(credentials)

    reddit = reddit_parser.reddit

    corona_json = reddit_parser.get_json_trees_by_subreddit("Coronavirus", 10)

    #conspiracy_json = reddit_parser.get_json_trees_by_subreddit("conspiracy", 10)
    
    if save_to_file:
        reddit_parser.write_json_to_file("coronavirus.json", corona_json)
        #reddit_parser.write_json_to_file("conspiracy.json", conspiracy_json)


  

    # ids = ["xkti8v", "xdn27t"]
    
   
