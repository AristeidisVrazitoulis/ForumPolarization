from tree_loader import TreeLoader
from perspective import PerspectiveAPI
import networkx as nx
from utils.post_id import *
import networkx as nx
import matplotlib.pyplot as plt

perspective = PerspectiveAPI()
def assign_sign_node(self, child, parent):
    if child.data["score"] <= 0 and parent.data["score"] <= 0:
        if perspective.is_prob_insult(child.data['body']) :
            child.data["score"] = -1

        if perspective.is_prob_insult(parent.data['body']):
            parent.data["score"] = -1


# takes as an input (a/many) treelib 
# returns a graph
def create_multigraph(reply_tree):
    ucg = nx.MultiDiGraph()
    
    for comment_node in reply_tree.all_nodes_itr():
        nid = comment_node.identifier
        child = reply_tree.get_node(nid)
        
        ucg.add_node(child.tag)
        parent = reply_tree.parent(nid)
        if parent is None:
            continue
        
        assign_sign_node(child, parent)
            

        # make a directed edge child -> parent
        ucg.add_edge(child.tag, parent.tag)
    return ucg


def draw_graph(ucg):
    nx.draw(ucg)
    plt.show()
        

if __name__ == "__main__":
    # filename = get_file_name(POST2)
    # tree_obj = TreeLoader()
    # tree_json = tree_obj.load_file(filename)
    # tree = tree_obj.load_tree(tree_json)
    # print(len(tree_obj.users))
    # ucg = create_multigraph(tree)
    # draw_graph(ucg)
    tree_loader = TreeLoader()
    filename = "conspiracy.json"
    trees = tree_loader.get_trees_from_json(filename)
    for tree in trees:
        ucg = create_multigraph(tree)

    # tree.show()













