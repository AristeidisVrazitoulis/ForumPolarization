'''
This file takes as an input a post id from reddit and saves the tree as json to disk
'''
import json
from treelib import Tree
from utils.settings import get_filenames_bysubreddit,categories
from extractor import Extractor
import reddit_instance

class RedditParser():

    
    def __init__(self, reddit):

        self.reddit = reddit
        self.categories = categories
        # self.keyword = keyword
       

    def write_json_to_file(self, filename, json_str):
        folder = r"tree_data/"
        path_name = folder+filename
        with open(path_name,"w") as f:
            f.write(json.dumps(json_str,indent=2))
        
    # takes a submissin id from a reddit post and returns a treelib object    
    def create_tree(self, submission_id):
        
        submission = self.reddit.submission(submission_id)
        submission.comments.replace_more(limit=4)
        tree = Tree()
        # root node
        tree.create_node(str(submission.author), str(submission.id), data={"score":submission.score,"body":submission.selftext, "submission_id":str(submission_id)}) 
        # traverse the tree
        for comment in submission.comments.list():
            comment_author = str(comment.author)
            if comment_author == "AutoModerator":continue
            author_name = comment_author+str(comment.id) if comment_author == "None" else comment_author

            parent_id = str(comment.parent_id[3:])
            if not tree.contains(parent_id):continue

            tree.create_node(
                author_name,    # tag
                str(comment.id),# identifier 
                parent=parent_id,
                data = {"body":comment.body, "score":comment.score}
            )
        return tree

    # takes a list of ids andd returns a set of trees (of comments) of treelib object
    def get_trees_by_id(self, ids):
        trees = set()
        for id in ids:
            trees.add(self.create_tree(id))
        return trees


    # extracts top submissions of a subreddit
    def extract_top_submissions(self, subreddit, keyword, limit):
        submission_ids = []
        submissions = subreddit.search(keyword, sort="top", limit=limit)
        for sub in submissions:
            submission_ids.append(sub.id)
        
        return submission_ids


    # extracts top submissions of a subreddit
    def extract_controversial_submissions(self, subreddit, keyword, limit):
        submission_ids = []
        submissions = subreddit.controversial(time_filter="all", limit = None)
               
        counter = 0
        for sub in submissions:
            text = sub.title.lower()+"\n"+sub.selftext.lower()
            if (keyword in text):
                submission_ids.append(sub.id)
                counter += 1
                if counter == limit:
                    break
        return submission_ids

      
    # puts all trees in a dictionary
    def create_merged_json(self, trees):
        # json_obj = {}
        ret_obj = {}
        for tree in trees:
            json_tree = json.loads(tree.to_json(with_data=True))
            root_name = tree.get_node(tree.root)
            json_obj = {root_name.tag : json_tree[root_name.tag]}
            ret_obj[root_name.identifier] = json_obj

        return ret_obj

    # takes subreddit and returns the set of post we define(category)
    def get_all_submissions(self, sub, keyword, limit, category="all"):
            
        if category != "controversial":
            top_posts = self.extract_top_submissions(sub, keyword, limit)
        if category != "top":
            controversial_posts = self.extract_controversial_submissions(sub, keyword, limit)

        if category == "top":
            return [top_posts]
        elif category == "controversial":
            return [controversial_posts]
        elif category=="both":
            return [top_posts, controversial_posts]
        elif category == "all":
            return [top_posts, controversial_posts, top_posts+controversial_posts]
        else:
            print("category not found")
            return None

    # takes a set of IDs and returns a corresponding json object
    def get_json_by_postids(self, post_ids):
        # a list of treelib objects
        trees = self.get_trees_by_id(post_ids)
        # makes a json dictionary with those trees
        json_dict = self.create_merged_json(trees)
        return json_dict
    
    # takes a subreddit name and returns 1 list of (3) lists of the ids
    def get_all_json_trees(self, subreddit_name, keyword, limit):
        json_trees = []
        sub = self.reddit.subreddit(subreddit_name)
        

        top_posts = self.extract_top_submissions(sub, keyword, limit)
        print(len(top_posts))
        top_trees = self.get_trees_by_id(top_posts)
        print("top", self.count_comms(top_trees))

        controversial_posts = self.extract_controversial_submissions(sub, keyword, limit)
        print(len(controversial_posts))
        controversial_trees = self.get_trees_by_id(controversial_posts)
        print("contro", self.count_comms(controversial_trees))

        all_trees = top_trees.union(controversial_trees)
        if len(top_trees.intersection(controversial_trees)) != 0:
            print("theres overlap between categories")
        
        json_trees.append(self.create_merged_json(top_trees))
        json_trees.append(self.create_merged_json(controversial_trees))
        json_trees.append(self.create_merged_json(all_trees))
        
        return json_trees

    def count_comms(self, trees):
        s = 0
        for t in trees:
            s += len(t.all_nodes())
        return s

    
    def save_trees_json_todisk(self, json_trees, names):
        for i in range(len(json_trees)):
            self.write_json_to_file("{}_{}.json".format(subreddit_name, names[i]), json_trees[i])

    def test1(self, subreddit_name, keyword, save_to_file):
        json_trees = self.get_all_json_trees(subreddit_name, keyword, limit)

        if save_to_file:
            self.save_trees_json_todisk(json_trees, self.categories)

    def test2(self, subreddit_name, keyword, save_to_file):
        sub = self.reddit.subreddit(subreddit_name)
        ids = self.extract_controversial_submissions(sub, keyword, limit)
        print(len(ids))
        extractor = Extractor(reddit, ids)
        json_tree = list(extractor.create_trees(ids))
        json_tree = self.create_merged_json(json_tree)


        if save_to_file:
            self.save_trees_json_todisk([json_tree], ["controversial11"])

    


if __name__ == "__main__":
    #settings
    
    reddit = reddit_instance.get_reddit_instance()
    save_to_file = True
    limit = 300
    subreddit_name = "Christianity"
    keyword = "god"

    reddit_parser = RedditParser(reddit)

    reddit_parser.test1(subreddit_name, keyword, save_to_file)
    # reddit_parser.test2(subreddit_name, keyword, save_to_file)
    
    
    

    
 

    
   
