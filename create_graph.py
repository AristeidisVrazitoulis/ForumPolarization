from deserialize_tree import DeserializeTree
import networkx as nx
from post_id import *



# takes as an input a treelib 
# returns a graph

def create_multigraph(reply_tree):
    ucg = nx.DiGraph()

    for comment_node in reply_tree.all_nodes_itr():
        nid = comment_node.identifier
        parent = reply_tree.parent(nid)
        if parent==None:
            continue
        child = reply_tree.get_node(nid)
        # make a directed edge  parent -> child
        ucg.add_edge(parent,child)

        

if __name__ == "__main__":
    filename = get_file_name(POST2)
    tree_obj = DeserializeTree()
    tree_json = tree_obj.load_file(filename)
    tree = tree_obj.load_tree(tree_json)
    create_multigraph(tree)
    tree.show()













