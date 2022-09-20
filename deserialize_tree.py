# deserialize
# takes as input a json tree file
import json
from treelib import Tree



def load_file(filename):
    # loads json file at the directory 'tree_data'
    with open("tree_data/{}".format(filename)) as f:
        tree_data = json.load(f)
    return tree_data

tree = Tree()
id = 0
users = {}
def load_tree(json_tree, parent=None):
    global id
    # deserializes json object and returns a treelib object
    node_name,_ = list(json_tree.items())[0]
    users.add(node_name)
    if "children" not in json_tree[node_name]:
        return tree
    
    if parent is None:
        tree.create_node(str(node_name), id)
        parent = 0    

    parent = id    
    for counter,value in enumerate(json_tree[node_name]['children']):  
        child = list(value)[0]
        child_data = value[child]["data"]
        id += 1
        tree.create_node(child, id, parent=parent, data={"body":child_data["body"],"score":child_data["score"]})
        load_tree(json_tree[node_name]['children'][counter], parent)
        
    return tree
    

d =["xdb9dj","xdn27t"]
big = 0
small = 1

if __name__ == "__main__":
    tree_json = load_file("tree_"+d[big]+".json")
    tree = load_tree(tree_json)
    tree.show()







