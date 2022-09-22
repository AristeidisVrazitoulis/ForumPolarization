from tree_loader import DeserializeTree, TreeLoader
import networkx as nx
from post_id import *
import networkx as nx
import matplotlib.pyplot as plt


# takes as an input (a/many) treelib 
# returns a graph
def create_multigraph(reply_tree):
    ucg = nx.MultiDiGraph()
    for comment_node in reply_tree.all_nodes_itr():
        nid = comment_node.identifier
        child = reply_tree.get_node(nid)
        ucg.add_node(child.tag)
        parent = reply_tree.parent(nid)
        if parent==None:
            continue
        
        # make a directed edge child -> parent
        ucg.add_edge(child.tag,parent.tag)
    
    return ucg


def draw_graph(ucg):
    nx.draw(ucg)
    plt.show()
        

if __name__ == "__main__":
    filename = get_file_name(POST2)
    tree_obj = TreeLoader()
    tree_json = tree_obj.load_file(filename)
    tree = tree_obj.load_tree(tree_json)
    print(len(tree_obj.users))
    ucg = create_multigraph(tree)
    draw_graph(ucg)
    # tree.show()













