'''
deserialize
this file takes as input a json file and can return a treelib object
'''
import json
from treelib import Tree



from utils.commons import get_filenames_by_subreddit
import copy

from preprocessing.reddit_scrape import reddit_instance
from utils import commons

class TreeLoader:
    
    def __init__(self):
        self.tree = Tree()
        # id of the node
        self.id = 0

    def initialize_tree(self):
        self.tree = Tree()
        # self.id = 0

    # returns json file
    def load_file(self,filename):
        # loads json file at the directory 'tree_data'
        
        with open("forum_polarization/preprocessing/tree_data/{}".format(filename)) as f:
            tree_data = json.load(f)
        return tree_data

    # returns a treelib object by taking as an input a json object
    def load_tree(self, json_tree, parent=None):

        # deserializes json object and returns a treelib object
        node_name,_ = list(json_tree.items())[0]

        # if it is a leaf
        if "children" not in json_tree[node_name]:
            return self.tree
        
        if parent is None:
            parent_data = json_tree[node_name]["data"]
            self.tree.create_node(str(node_name), self.id,data=parent_data)
            parent = 0    

        parent = self.id    
        for counter,value in enumerate(json_tree[node_name]['children']):  
            child_name = list(value)[0]
            child_data = value[child_name]["data"]
            self.id += 1
            self.tree.create_node(
                child_name, 
                self.id, 
                parent=parent, 
                data={"body":child_data["body"],"score":child_data["score"]}
            )
            self.load_tree(json_tree[node_name]['children'][counter], parent)
            
        return self.tree    

    # returns a list of treelib objects by reading json file
    def get_trees_from_json(self, filename):
        trees = []
        tree_json = self.load_file(filename)

        for tree_item in tree_json.items():
            self.initialize_tree()
            
            tree_item = tree_item[1]
            tree = self.load_tree(tree_item)
            # need of deep copying cause  we have one instance of Tree()
            trees.append(copy.deepcopy(tree))
        
        return trees

    def get_modifed_trees_from_json(self, filename):
        trees =  self.get_trees_from_json(filename)
        new_trees = []
        # modify the trees
        for reply_tree in trees:
            if reply_tree.root is None: continue
            root_node = reply_tree.get_node(reply_tree.root)
            modified_tree = Tree()
            # create the root node
            modified_tree.create_node(root_node.tag, root_node.identifier, data=root_node.data)

            visited = set()
            for comment_node in reply_tree.all_nodes_itr():
                nid = comment_node.identifier
                if nid == root_node.identifier or comment_node.tag in visited:continue
                visited.add(comment_node.tag)
                # parent is always root
                modified_tree.create_node(comment_node.tag, comment_node.identifier, data=comment_node.data, parent=root_node.identifier)
            new_trees.append(modified_tree)
            
        return new_trees

    # takes a set of filenames opens them and counts
    def count_comments(self, filenames):
        d = {}
        for filename in filenames:
            num_comments = 0
            trees = self.get_trees_from_json(filename)
            for tree in trees:
                s = len(tree.all_nodes())
                num_comments += s
            d[filename] = num_comments
        return d


    def count_trees(self, filenames):
        d = {}
        for filename in filenames:
            trees = self.get_trees_from_json(filename)
            d[filename] = len(trees)
        return d

    # only for debugging
    def get_submissions(self, filename):
        ids = set()
        trees = self.get_trees_from_json(filename)
        for tree in trees:
            root = tree.get_node(tree.root)
            print(root.tag)
            ids.add(root)
            
        return ids
    
    def test1(self, f1, f2):
        
        id_set1 = self.get_submissions(f1)
        id_set2 = self.get_submissions(f2)
        print(len(id_set1))
        print(len(id_set2))
        all_trees = id_set1.intersection(id_set2)
        print(all_trees)

        #reddit_parse = reddit_parser.RedditParser()
        #json_str = reddit_parse.create_merged_json(all_trees)
        #reddit_parse.write_json_to_file("{}_{}.json".format(subreddit_name, "both"), json_str)




if __name__ == "__main__":
    
    
    # reddit = reddit_instance.get_reddit_instance()
    # redit_parse = reddit_parser.RedditParser(reddit)
    
    tree_loader = TreeLoader()
    subreddit_name = "space"

    filenames = get_filenames_by_subreddit(subreddit_name, "json")  

    
    print(tree_loader.count_trees(filenames))
    print(tree_loader.count_comments(filenames))

    # print(len(tree_loader.users))
    # tree_loader.test1(filenames[0],filenames[1], subreddit_name)



