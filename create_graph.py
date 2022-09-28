from tree_loader import TreeLoader
from perspective import PerspectiveAPI
import networkx as nx
from utils.post_id import *
import networkx as nx
import matplotlib.pyplot as plt


class UserGraph:

    def __init__(self):
        self.perspective = PerspectiveAPI()


    def determine_edge_sign(self, child, parent):
        # child.data["score"] = -1 if child.data["score"] < 0 else 1
        edge_sign = child.data["score"]*parent.data["score"]
        #asssign edge sign
        if child.data["score"] < 0 and parent.data["score"] < 0:
            if self.perspective.is_prob_insult(child.data["body"]):
                print(child.data["body"])
                print("-------------")
                edge_sign = -1
        return edge_sign
        

    def aggregate_graphs(self, graphs):
        pass
    # takes as an input (a/many) treelib 
    # returns a graph
    def create_multigraph(self, reply_tree):
        ucg = nx.MultiDiGraph()
        
        for comment_node in reply_tree.all_nodes_itr():
            nid = comment_node.identifier
            child = reply_tree.get_node(nid)
            child.data["score"] = -1 if child.data["score"] < 0 else 1
            ucg.add_node(child.tag)

            parent = reply_tree.parent(nid)
            if parent is None: continue
            
            edge_sign = self.determine_edge_sign(child, parent)
            # make a directed edge child -> parent
            ucg.add_edge(child.tag, parent.tag, weight=edge_sign)
        return ucg


    def draw_graph(self, ucg):
        nx.draw(ucg)
        plt.show()
        

if __name__ == "__main__":
   
    tree_loader = TreeLoader()
    graph = UserGraph()
    filename = "conspiracy.json"
    trees = tree_loader.get_trees_from_json(filename)
    ucgs = []
    for tree in trees:
        ucg = graph.create_multigraph(tree)
        ucgs.append(ucg)
















