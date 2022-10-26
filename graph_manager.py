from httplib2 import ServerNotFoundError
from perspective import PerspectiveAPI
import networkx as nx
from utils.post_id import *
import networkx as nx
from utils.get_filenames import get_filenames_bysubreddit
from tree_loader import TreeLoader

import time


class GraphManager:

    # takes as input a comment and the answer of the comment
    # and determines the sign of the edge
    def determine_edge_sign(self, child, parent, perspective):
        edge_sign = child.data["score"]*parent.data["score"]
        # assign edge sign
        if child.data["score"] < 0 and parent.data["score"] < 0:
            if perspective.is_prob_insult(child.data["body"]):
                print(child.data["body"])
                print("-------------")
                edge_sign = -1
            # limit of 1 request per second
            time.sleep(1.05)
            
        return edge_sign

    def get_perspective_api(self):
        try:
            return PerspectiveAPI()
        except ServerNotFoundError:
            print("No wifi")
            return None
        

    def aggregate_graphs(self, graphs):
        pass

    # takes as an input a treelib 
    # returns a multigraph
    def create_multigraph(self, reply_tree):
        ucg = nx.MultiDiGraph()
        perspective = self.get_perspective_api()
        if perspective is None:return

        for comment_node in reply_tree.all_nodes_itr():
            nid = comment_node.identifier
            child = reply_tree.get_node(nid)
            child.data["score"] = -1 if child.data["score"] < 0 else 1
            ucg.add_node(child.tag)

            parent = reply_tree.parent(nid)
            if parent is None: continue
            
            edge_sign = self.determine_edge_sign(child, parent, perspective)
            # make a directed edge child -> parent
            ucg.add_edge(child.tag, parent.tag, weight=edge_sign)
        return ucg

    def merge_graphs(self, graphs):
        g = graphs[0]
        for i in range(1,len(graphs)):
            g = nx.compose(g, graphs[i]) 
        return g

    # merges all trees given from a file
    # returns an nx graph
    def get_unified_graph_from_file(self, filename):
        tree_loader = TreeLoader()
        trees = tree_loader.get_trees_from_json(filename)
        ucgs = []
        for tree in trees:
            ucg = self.create_multigraph(tree)
            ucgs.append(ucg)

        return self.merge_graphs(ucgs)


    def export_graph(self, graph, filename, data=False):
        filepath = "graph_data/{}".format(filename)
        nx.write_edgelist(graph, filepath, data=data)

    def import_graph(self, filename):
        filepath = "graph_data/{}".format(filename)
        return nx.read_edgelist(filepath)

    def combine_graphs_from_file(self, filename1, filename2):
        graph1 = self.import_graph(filename1)
        graph2 = self.import_graph(filename2)
        # tups = community.kernighan_lin_bisection(graph1)
        setA = set(graph1.nodes)
        setB = set(graph2.nodes)
        setC = setA.intersection(setB)
        print(len(setC))

        merged = self.merge_graphs([graph1, graph2])

        self.export_graph(merged, "{}_{}.txt".format(filename1, filename2))


    def print_graph_stats(self, subr):
        filenames = get_filenames_bysubreddit(subr,"txt")
        for filename in filenames:
            g = manager.import_graph(filename)
            print(filename)
            print("#nodes:",len(g.nodes))
            print("#edges:",len(g.edges))
            print()

    # loads trees from disk and saves an nx graph to disk
    def load_trees_save_to_disk(self, subreddit_name):
        filenames = get_filenames_bysubreddit(subreddit_name, "json")
        for filename in filenames:
            print(filename)
            g = self.get_unified_graph_from_file(filename)
            self.export_graph(g, filename.split(".")[0]+".txt")

        

if __name__ == "__main__":
   
    manager = GraphManager()
    # filename = "conspiracy_both.json"

    subreddit = "DebateVaccines"

    manager.load_trees_save_to_disk(subreddit)
    manager.print_graph_stats(subreddit)
    



    
    # graph = manager.import_graph("merged.txt")

    # print(len(graph.nodes))
    # print(len(graph.edges))
    
