'''
deserialize
this file takes as input a json file and can return a treelib object
'''
import json
from treelib import Tree
import copy

class TreeLoader:
    
    def __init__(self):
        self.tree = Tree()
        # id of the node
        self.id = 0
        self.users = set()

    def initialize_tree(self):
        self.tree = Tree()
        self.id = 0

    # returns json file
    def load_file(self,filename):
        # loads json file at the directory 'tree_data'
        with open("tree_data/{}".format(filename)) as f:
            tree_data = json.load(f)
        return tree_data

    # returns a treelib object by taking as an input a json object
    def load_tree(self, json_tree, parent=None):
        # deserializes json object and returns a treelib object
        node_name,_ = list(json_tree.items())[0]
        self.users.add(node_name)
        if "children" not in json_tree[node_name]:
            return self.tree
        
        if parent is None:
            self.tree.create_node(str(node_name), self.id)
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
            json_tree = {tree_item[0] : tree_item[1]}
            tree = self.load_tree(json_tree)
            # need of deep copying cause  we have one instance of Tree()
            trees.append(copy.deepcopy(tree))
        
        return trees
        

if __name__ == "__main__":
    tree_loader = TreeLoader()
    filename = "coronavirus.json"
    trees = tree_loader.get_trees_from_json(filename)








