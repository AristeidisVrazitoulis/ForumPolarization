from tree_loader import TreeLoader
from perspective import PerspectiveAPI
import networkx as nx
from utils.post_id import *
import networkx as nx
import matplotlib.pyplot as plt


class GraphManager:

    def __init__(self):
        self.perspective = PerspectiveAPI()

    # takes as input a comment and the answer of the comment
    # and determines the sign of the edge
    def determine_edge_sign(self, child, parent):
        edge_sign = child.data["score"]*parent.data["score"]
        # assign edge sign
        if child.data["score"] < 0 and parent.data["score"] < 0:
            if self.perspective.is_prob_insult(child.data["body"]):
                print(child.data["body"])
                print("-------------")
                edge_sign = -1
        return edge_sign
        

    def aggregate_graphs(self, graphs):
        pass

    # takes as an input a treelib 
    # returns a multigraph
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

    def merge_graphs(self, graphs):
        g = graphs[0]
        for i in range(1,len(graphs)):
            g = nx.compose(g, graphs[i]) 
        return g

    def export_graph(self, graph, filename, data=False):
        filepath = "graph_data/{}".format(filename)
        nx.write_edgelist(graph, filepath, data=data)

    def import_graph(self, filename):
        filepath = "graph_data/{}".format(filename)
        return nx.read_edgelist(filepath)


    def draw_graph(self, ucg):
        nx.draw(ucg, node_size=30)
        plt.show()
        

if __name__ == "__main__":
   
    # tree_loader = TreeLoader()
    manager = GraphManager()
    # filename = "coronavirus.json"

    # trees = tree_loader.get_trees_from_json(filename)
    # ucgs = []
    
    # for tree in trees:
    #     ucg = manager.create_multigraph(tree)
    #     ucgs.append(ucg)

    # unified_graph = manager.merge_graphs(ucgs)
    # manager.export_graph(unified_graph, "coronavirus_unified.el")

    corona_graph = manager.import_graph("coronavirus_unified.el")
    manager.draw_graph(corona_graph)
    # conspiracy_graph = manager.import_graph("conspiracy_unified.el")
