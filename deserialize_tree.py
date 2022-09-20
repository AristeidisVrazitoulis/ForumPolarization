'''
deserialize
this file takes as input a json file and can return a treelib object
'''
import json
from treelib import Tree


class DeserializeTree:
    
    def __init__(self):
        self.tree = Tree()
        # id of the node
        self.id = 0
        self.users = set()

    # TEMPORARY
    def initialize_tree(self):
        self.tree = Tree()

    # returns json file
    def load_file(self,filename):
        # loads json file at the directory 'tree_data'
        with open("tree_data/{}".format(filename)) as f:
            tree_data = json.load(f)
        return tree_data

    # returns a treelib object
    def load_tree(self,json_tree, parent=None):
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
            child = list(value)[0]
            child_data = value[child]["data"]
            self.id += 1
            self.tree.create_node(
                child, 
                self.id, 
                parent=parent, 
                data={"body":child_data["body"],"score":child_data["score"]}
                )
            self.load_tree(json_tree[node_name]['children'][counter], parent)
            
        return self.tree
    



if __name__ == "__main__":
    from  post_id import *
    deserialize = DeserializeTree()
    tree_json = deserialize.load_file(get_file_name(POST2))
    tree = deserialize.load_tree(tree_json)
    tree.show()







