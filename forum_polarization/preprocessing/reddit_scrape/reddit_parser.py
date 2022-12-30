'''
This file takes as an input a post id from reddit and saves the tree as json to disk
'''



from treelib import Tree

from utils import commons

import json
import reddit_instance
import os

class RedditParser():

    
    def __init__(self, reddit):

        self.reddit = reddit
        self.categories = commons.categories
       

    def write_json_to_file(self, filename, json_str):
        folder = "../tree_data/"
        path_name = folder+filename
        if os.path.exists(path_name):
            filename_parts = filename.split("_")
            digit = 0
            if filename_parts[0][-1].isdigit():
                digit = int(filename_parts[0][-1])+1
            filename = filename_parts[0]+str(digit)+"_"+filename_parts[1]
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
        submissions = subreddit.search(keyword, time_filter="all", limit=limit)
        for sub in submissions:
            submission_ids.append(sub.id)
        
        return submission_ids


    # extracts top submissions of a subreddit
    def extract_controversial_submissions(self, subreddit, keyword, limit):
        submission_ids = []
        submissions = subreddit.controversial(time_filter="all", limit = limit)
               
        counter = 0
        for sub in submissions:
            text = sub.title.lower()+"\n"+sub.selftext.lower()
            if ("moon" in text):
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


    # takes a set of IDs and returns a corresponding json object
    def get_json_by_postids(self, post_ids):
        # a list of treelib objects
        trees = self.get_trees_by_id(post_ids)
        # makes a json dictionary with those trees
        json_dict = self.create_merged_json(trees)
        return json_dict
    
    # returns a set of tree objects by category
    def get_category_trees(self, subreddit, keyword, limit, category):
        if category == "top":
            posts = self.extract_top_submissions(subreddit, keyword, limit)
        elif category == "controversial":
            posts = self.extract_controversial_submissions(subreddit, keyword, limit)

        print("# posts",len(posts))
        trees = self.get_trees_by_id(posts)
        print(category,"# comments:", self.count_comms(trees))
        return trees
        

    # takes a subreddit name and returns 1 list of (3) lists of the ids
    def get_all_json_trees(self, subreddit, keyword, limit):
        json_trees = []
        
        top_trees = self.get_category_trees(subreddit, keyword, limit, "top")
        controversial_trees = self.get_category_trees(subreddit, keyword, limit, "controversial")
        all_trees = top_trees.union(controversial_trees)
        if len(top_trees.intersection(controversial_trees)) != 0:
            print("theres overlap between categories")

        all_trees = [top_trees, controversial_trees, all_trees]

        for tree_set in all_trees:
            json_trees.append(self.create_merged_json(tree_set))
        
        return json_trees
    
    def get_specific_json_trees(self, categories, subreddit, keyword, limit):
        pass

    def find_controversial_posts(self, subreddit, keyword):
        # time_filters = ["all", "month", "week", "day"]
        submission_ids = []
        submissions = subreddit.search(keyword, sort="top", time_filter="all", limit=limit)
        for sub in submissions:
            current_sub = reddit.submission(sub.id)

            if current_sub.upvote_ratio < 0.7:
                print("bingo")
                submission_ids.append(sub.id)
        
        print(len(submission_ids))
        return submission_ids
        
    def count_comms(self, trees):
        n_comments = 0
        for t in trees:
            n_comments += len(t.all_nodes())
        return n_comments

    
    def save_trees_json_todisk(self, json_trees, names):
        for i in range(len(json_trees)):
            self.write_json_to_file("{}_{}.json".format(subreddit_name, names[i]), json_trees[i])

    def test1(self, subreddit_name, keyword, save_to_file):
        subreddit = self.reddit.subreddit(subreddit_name)
        json_trees = self.get_all_json_trees(subreddit, keyword, limit)

        if save_to_file:
            self.save_trees_json_todisk(json_trees, self.categories)

    


if __name__ == "__main__":
    #settings
    
    reddit = reddit_instance.get_reddit_instance()
    save_to_file = True
    limit = 500
    subreddit_name = "space"
    keyword = "moon landing"

    reddit_parser = RedditParser(reddit)
    subreddit = reddit.subreddit(subreddit_name)


    reddit_parser.test1(subreddit_name, keyword, save_to_file)
    # print(len(reddit_parser.extract_controversial_submissions(subreddit,keyword,limit)))
    
    

    
 

    
   
