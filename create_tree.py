'''
This file takes as an input a post id from reddit and saves the tree as json to disk
'''
import json
import praw
from treelib import Tree


def write_json_to_file(filename, tree):
    folder = r"tree_data/"
    path_name = folder+filename
    with open(path_name,"w") as f:
        f.write(tree.to_json(with_data=True))
    tree.save2file(path_name+".txt")
    
    
def create_tree(reddit, submission_id):
    submission = reddit.submission(submission_id)
    submission.comments.replace_more(limit=None)
    tree = Tree()
    # root node
    tree.create_node(str(submission.author), str(submission.id)) 
    #traverse the tree
    for comment in submission.comments.list():
        tree.create_node(
            str(comment.author),
            str(comment.id), 
            parent=str(comment.parent_id[3:]),
            data = {"body":comment.body, "score":comment.score}
        )
    return tree


def get_reddit_instance(credentials):

    with open(credentials) as f:
        creds = json.load(f)
        
    # create reddit instance
    reddit = praw.Reddit(client_id=creds['client_id'],
                        client_secret=creds['client_secret'],
                        user_agent=creds['user_agent'],
                        redirect_uri=creds['redirect_uri'],
                        refresh_token=creds['refresh_token'])
    return reddit



if __name__=="__main__":
    #settings
    credentials = 'client_secrets.json'
    submission_id = "xdb9dj"

    reddit = get_reddit_instance(credentials)
    tree = create_tree(reddit, submission_id)
    write_json_to_file("tree_{}.json".format(submission_id), tree)