'''
Format:
1 JSON file has multiple trees
For each JSON file we make a graph for each tree and then merge all those graphs
'''


import networkx as nx
import time

from httplib2 import ServerNotFoundError
from perspective import PerspectiveAPI
from utils.post_id import *
from utils.settings import get_filenames_bysubreddit
from tree_loader import TreeLoader
from networkx.algorithms import community


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
            if child.tag == "AutoModerator":continue
            child.data["score"] = -1 if child.data["score"] < 0 else 1
            ucg.add_node(child.tag)

            parent = reply_tree.parent(nid)
            if parent is None or parent.tag == "AutoModerator": continue
            if parent is None: continue
            
            # edge_sign = self.determine_edge_sign(child, parent, perspective)
            edge_sign = 1

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
        return nx.MultiDiGraph(nx.read_edgelist(filepath))

    def combine_graphs_from_file(self, filename1, filename2):
        graph1 = self.import_graph(filename1)
        graph2 = self.import_graph(filename2)
        # tups = community.kernighan_lin_bisection(graph1)
        setA = set(graph1.nodes)
        setB = set(graph2.nodes)
        setC = setA.intersection(setB)
        print("intersection exists", len(setC))

        merged = self.merge_graphs([graph1, graph2])
        filename1 = filename1.split(".")[0]
        filename2 = filename2.split(".")[0]
        graph_name =  "{}_{}.txt".format(filename1, filename2)
        merged = self.get_connected_graph(merged)

        self.partition_and_save(merged, graph_name)

        self.export_graph(merged, graph_name)

    def print_single_graph(self, graph):
        print(graph, "denstity:", round(nx.density(graph),4))

    def print_graph_stats(self, subr):
        filenames = get_filenames_bysubreddit(subr,"txt")
        for filename in filenames:
            g = manager.import_graph(filename)
            self.print_single_graph(g)
            print()

    def get_largest_connected_graph(self, graph):
        components = nx.weakly_connected_components(graph)
        largest_cc = list(max(components, key=len))
        return graph.subgraph(largest_cc)
            
    def get_connected_graph(self, g):
        if not nx.is_weakly_connected(g):
            print("graph is not connected")
            g = self.get_largest_connected_graph(g)
            self.print_single_graph(g)
        return g


    # loads trees from disk and saves an nx graph to disk
    def load_tree_save_to_disk(self, filename):
        
        print(filename)
        g = self.get_unified_graph_from_file(filename)
        self.print_single_graph(g)
        g = self.get_connected_graph(g)
        print("h",g)
        self.export_graph(g, filename.split(".")[0]+".txt")

    def bisect_graph(self, G):
        if nx.is_directed(G):
            G = nx.Graph(G)
        groupA, groupB = community.kernighan_lin_bisection(G)
        return (groupA, groupB)
    
    def save_partitions(self, graph_name, groupA, groupB):
        filepath = "graph_data/graph_partitions/{}".format(graph_name)
        # convert to list
        groupA, groupB = list(groupA), list(groupB)
        print(len(groupA), len(groupB))

        min_length = min(len(groupA), len(groupB))
        with open(filepath, "w") as f:
            for i in range(min_length):
                f.write(f"{groupA[i]},{groupB[i]}\n")

            # for i in range(min_length, len(groupB)): .. 
            if len(groupA) > len(groupB):
                f.write(f"{groupA[len(groupA)-1]},")
            elif len(groupA) < len(groupB):
                f.write(f",{groupB[len(groupB)-1]}")


    def load_partitions(self, graph_name):
        filepath = "graph_data/graph_partitions/{}".format(graph_name)
        groupA = set()
        groupB = set()
        with open(filepath, "r") as f:
            for line in f.readlines():
                users = line.split(",")
                if users[0] == "":
                    groupB.add(users[1])
                elif users[1] == "":
                    groupA.add(users[0])
                else:
                    groupA.add(users[0])
                    groupB.add(users[1])
        print(len(groupA),len(groupB))
        return (groupA, groupB)


    def partition_and_save(self, G, graph_name):
        groupA, groupB = self.bisect_graph(G)
        self.save_partitions(graph_name, groupA, groupB)


    def test1_save_graphs(self, sub_name):
        filenames = get_filenames_bysubreddit(sub_name, "json")
        for filename in filenames:
            self.load_tree_save_to_disk(filename)

    def test2_save_partitions(self, sub_name):
        filenames = get_filenames_bysubreddit(sub_name, "txt")
        for filename in filenames:
            
            G = self.import_graph(filename)
            self.partition_and_save(G, filename)

    def test3_load_partitions(self, sub_name):
        filenames = get_filenames_bysubreddit(sub_name, "txt")
        for filename in filenames:
            self.load_partitions(filename)
 

if __name__ == "__main__":
   
    manager = GraphManager()
    # filename = "conspiracy_both.json"

    subreddit = "conspiracy"
    
    manager.test1_save_graphs(subreddit)
    # manager.test2_save_partitions(subreddit)
    # print()
    # manager.test3_load_partitions(subreddit)

    # manager.combine_graphs_from_file("personalfinance_controversial.txt", "wallstreetbets_controversial.txt")

    # manager.load_bisections("Coronavirus_controversial")




    

    
