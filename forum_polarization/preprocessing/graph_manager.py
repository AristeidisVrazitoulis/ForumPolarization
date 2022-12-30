'''
Format:
1 JSON file has multiple trees
For each JSON file we make a graph for each tree and then merge all those graphs
'''


import networkx as nx
import time

from httplib2 import ServerNotFoundError


from utils import commons
from preprocessing.perspective_api import perspective

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
                # print(child.data["body"])
                # print("-------------")
                edge_sign = -1
                self.count_hate_comments += 1
            # limit of 1 request per second
            time.sleep(1.05)
            
        return edge_sign

    def get_perspective_api(self):
        try:
            return perspective.PerspectiveAPI()
        except ServerNotFoundError:
            print("No wifi")
            return None
        

    # converts multidigraph to graph just by adding edges
    def aggregate_graph(self, multi_graph):
        # create weighted graph from M
        G = nx.Graph()
        for u,v in multi_graph.edges():
            # w = data['weight'] if 'weight' in data else 1.0
            if G.has_edge(u,v):
                G[u][v]['weight'] += 1
            else:
                G.add_edge(u, v, weight=1)

        return G

    def make_probability_graph(self, graph):
        G = nx.DiGraph(graph)
        for node in G.nodes():
            s = sum([G[node][n]['weight'] for n in G[node]])
            for neighbour in G[node]:
                    G[node][neighbour]['weight'] /= s
        return G


    # converts multidigraph to graph just by adding edges
    def aggregate_signed_graph(self, multi_graph):
        # create weighted graph from M
        G = nx.Graph()
        for u,v,data in multi_graph.edges(data=True):
            w = data['weight']
            if G.has_edge(u,v):
                if G[u][v]['weight'] == -1: continue

                G[u][v]['weight'] = w
            else:
                G.add_edge(u, v, weight=w)

        return G


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
    def create_graph_from_trees(self, trees):
        
        ucgs = []
        for tree in trees:
            ucg = self.create_multigraph(tree)
            ucgs.append(ucg)

        return self.merge_graphs(ucgs)


    def export_graph(self, graph, filename, specific_path=""):
        if specific_path != "":
            filepath = specific_path
        filepath = "forum_polarization/preprocessing/graph_data/{}".format(filename)
        nx.write_weighted_edgelist(graph, filepath)

    def import_graph(self, filename, specific_path="", weighted=False):
        if specific_path != "":
            filepath = specific_path
        filepath = "forum_polarization/preprocessing/graph_data/{}".format(filename)
        if weighted:
            return nx.read_weighted_edgelist(filepath, create_using=nx.DiGraph)
        return nx.read_weighted_edgelist(filepath, create_using=nx.MultiDiGraph)

    def combine_graphs(self, graph1, graph2, weighted=False):
        # tups = community.kernighan_lin_bisection(graph1)
        setA = set(graph1.nodes)
        setB = set(graph2.nodes)
        setC = setA.intersection(setB)
        print("intersection exists", len(setC))

        merged = self.merge_graphs([graph1, graph2])
        
        merged = self.get_connected_graph(merged)

        return merged

    def print_single_graph(self, graph):
        print(graph)

    def print_graph_stats(self, subr):
        filenames = commons.get_filenames_by_subreddit(subr,"txt")
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


    # loads trees from disk and makes a graph
    def get_graph_from_file(self, filename, modified=False):
        
        tree_loader = TreeLoader()
        print(filename)
        if modified:
            trees = tree_loader.get_modifed_trees_from_json(filename)
        else:
            trees = tree_loader.get_trees_from_json(filename)

        self.count_hate_comments = 0
        g = self.create_graph_from_trees(trees)
        print("# hate comments", self.count_hate_comments)

        self.print_single_graph(g)
        # The graph might not be connected so we take the largest component of the graph
        g = self.get_connected_graph(g)

        print("connected component", g)
        print()
        return g
        # self.export_graph(g, filename.split(".")[0]+".txt")

    def bisect_graph(self, G):
        if nx.is_directed(G):
            G = nx.Graph(G)
        groupA, groupB = community.kernighan_lin_bisection(G)
        return (groupA, groupB)
    
    def calculate_average_degree(self, G):
        return sum([node[1] for node in G.degree])/len(G.degree)
    
    def calculate_clustering_coefficient(self, G):
        coeffs = nx.clustering(G)
        return sum(coeffs.values())/len(coeffs)



    def test1_save_graphs(self, sub_name, modify):
        filenames = commons.get_filenames_by_subreddit(sub_name, "")
        for filename in filenames:
            connected_graph = self.get_graph_from_file(filename + ".json", modify)
            if modify:
                filename=filename+"_modified"
            self.export_graph(connected_graph, filename+".txt")
    
    def test2_save_probability_graphs(self, sub_name):
        
        filenames = commons.get_filenames_by_subreddit(sub_name, "txt")
        for file in filenames:
            graph = manager.import_graph(file)
            new_graph = manager.aggregate_graph(graph)
            new_graph = manager.make_probability_graph(new_graph)
            manager.export_graph(new_graph, f"weighted_graphs/{file}")

    def test3_save_signed_graphs(self, sub_name):
        
        filenames = commons.get_filenames_by_subreddit(sub_name, "txt")
        for file in filenames:
            graph = manager.import_graph(file)
            new_graph = manager.aggregate_signed_graph(graph)
            manager.export_graph(new_graph, f"signed_graphs/{file}")

    def test4_combine_graphs(self, filename1, filename2):
        graph1 = self.import_graph(filename1)
        graph2 = self.import_graph(filename2)

        merged = self.combine_graphs(graph1, graph2)
        filename1 = filename1.split(".")[0]
        filename2 = filename2.split(".")[0]
        graph_name =  "{}_{}.txt".format(filename1, filename2)
        self.export_graph(merged, graph_name)




    def test5_save_interweighted_graphs(self, filename1, filename2):
        graph1 = self.import_graph(filename1)
        graph2 = self.import_graph(filename2)
        merged = self.combine_graphs(graph1, graph2)
        print(merged)
        aggregated_graph = self.aggregate_graph(merged)
        probability_graph = self.make_probability_graph(aggregated_graph)

        filename1 = filename1.split(".")[0]
        filename2 = filename2.split(".")[0]
        graph_name =  "{}_{}.txt".format(filename1, filename2)
        manager.export_graph(probability_graph, f"weighted_graphs/{graph_name}")




if __name__ == "__main__":
   
    manager = GraphManager()
    # filename = "conspiracy_both.json"

    for sub in commons.all_subreddits:

        names = commons.get_filenames_by_subreddit(sub,"txt",True)
        for name in names:
            g = manager.import_graph(name)
            g = nx.Graph(g)
            print(name,g)
            print(manager.calculate_average_degree(g))
            print()

    # manager.test1_save_graphs(sub, modify)


    # manager.test5_save_interweighted_graphs("conspiracy0_both.txt", "space_both.txt")
    # manager.test4_combine_graphs("conspiracy0_top.txt", "space_top.txt")
    # for sub in commons.all_subreddits:
    #     manager.test2_save_probability_graphs(sub)
    





    

    
