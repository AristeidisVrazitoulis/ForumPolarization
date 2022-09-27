from tree_loader import TreeLoader
from perspective import PerspectiveAPI
import networkx as nx
from utils.post_id import *
import networkx as nx
import matplotlib.pyplot as plt

perspective = PerspectiveAPI()

# takes as an input (a/many) treelib 
# returns a graph
def create_multigraph(reply_tree):
    ucg = nx.MultiDiGraph()
    
    for comment_node in reply_tree.all_nodes_itr():
        nid = comment_node.identifier

        child = reply_tree.get_node(nid)
       

        child.data["score"] = -1 if child.data["score"] < 0 else 1
        ucg.add_node(child.tag)

        parent = reply_tree.parent(nid)
        if parent is None:
            continue
                    
        
        # child.data["score"] = -1 if child.data["score"] < 0 else 1
        edge_sign = child.data["score"]*parent.data["score"]
        #asssign edge sign
        if child.data["score"] < 0 and parent.data["score"] < 0:
            if perspective.is_prob_insult(child.data["body"]):
                edge_sign = -1

        # make a directed edge child -> parent
        ucg.add_edge(child.tag, parent.tag, weight=edge_sign)
    return ucg


def draw_graph(ucg):
    nx.draw(ucg)
    plt.show()
        

if __name__ == "__main__":
   
    tree_loader = TreeLoader()
    filename = "conspiracy.json"
    trees = tree_loader.get_trees_from_json(filename)
    for tree in trees:
        ucg = create_multigraph(tree)
    
        # draw_graph(ucg)

    # tree.show()













