'''
Format:
1 JSON file has multiple trees
For each JSON file we make a graph for each tree and then merge all those graphs
'''


import networkx as nx
import time

from utils import commons
# from preprocessing.apis import perspective
from preprocessing.apis import sentiment_classifier

from preprocessing.tree_loader import TreeLoader
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
        pass
        # return perspective.PerspectiveAPI()
        
    
    def get_monkeylearn_api(self):
        pass
        

    # converts multidigraph to graph just by adding edges
    def aggregate_to_weighted_graph(self, multi_graph):
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

                G[u][v]['weight'] = 1
            else:
                if w == 0: w = 1
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
            
            edge_sign = self.determine_edge_sign(child, parent, perspective)
            # edge_sign = 1

            # make a directed edge child -> parent
            ucg.add_edge(child.tag, parent.tag, weight=edge_sign)
        return ucg

    def create_sentiment_multigraph(self, reply_tree):
        ucg = nx.MultiDiGraph()
        ml = sentiment_classifier.SentimentClassifier()
        for comment_node in reply_tree.all_nodes_itr():
            nid = comment_node.identifier
            child = reply_tree.get_node(nid)
            if child.tag == "AutoModerator":continue
            # assign score through sentiment analysis
            if child.data['body']:
                child_sign = ml.vader_classify(child.data['body'])
            else:
                child_sign = 1 if child.data['score'] > 0 else -1

            child.data["score"] = -1 if child.data["score"] < 0 else 1
            if child_sign == child.data['score']:
                self.count_same_signs += 1

            ucg.add_node(child.tag)

            parent = reply_tree.parent(nid)
            if parent is None or parent.tag == "AutoModerator": continue
            
            sign = child_sign*parent.data["score"]
            if  sign != 0:
                edge_sign = sign
            else: 
                edge_sign = child_sign+parent.data["score"]
            
            # edge_sign = 1

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
    def create_graph_from_trees(self, trees, sentiment=False):
        
        ucgs = []
        for tree in trees:
            if sentiment:
                ucg = self.create_sentiment_multigraph(tree)
            else:
                ucg = self.create_multigraph(tree)

            ucgs.append(ucg)

        return self.merge_graphs(ucgs)


    def export_graph(self, graph, filename="", specific_path=""):
        if specific_path != "":
            filepath = specific_path
        else:
            filepath = "forum_polarization/preprocessing/graph_data/{}".format(filename)
        nx.write_weighted_edgelist(graph, filepath)

    def import_graph(self, filename="", specific_path="", weighted=False):
        
        if specific_path != "":
            filepath = specific_path
        else:
            filepath = "graph_data/{}".format(filename)
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
    def get_graph_from_file(self, filename, modified=False, sentiment=False):
        
        tree_loader = TreeLoader()
        print(filename)
        if modified:
            trees = tree_loader.get_modifed_trees_from_json(filename)
        else:
            trees = tree_loader.get_trees_from_json(filename)

        self.count_hate_comments = 0
        self.count_same_signs = 0
        g = self.create_graph_from_trees(trees, sentiment)
        print(self.count_same_signs)


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
    
    def count_edges_across(self, g1_nodes, g2_nodes, merged_graph):
        count_edges = 0
        for u,v in merged_graph.edges():
            if (u in g1_nodes and v in g2_nodes) or (v in g1_nodes and u in g2_nodes):
                count_edges += 1

        return count_edges

    # converts names of to numbers 
    def modify_signed_format(self, sub):
        filename = f"graph_data/sentiment_graphs/{sub}_both.txt"

        name_graph = nx.read_weighted_edgelist(filename)

        nodes = list(name_graph.nodes)
        n_nodes = len(nodes)

        node_map = {nodes[i]:i for i in range(len(nodes))}
        
        with open(f"graph_data/sentiment_graphs/converted_graphs/{sub}.txt", 'w') as f1, open(filename, 'r') as f2:
            f1.write("#\t{}\n".format(n_nodes))
            for line in f2.readlines():
                edges = line.split()
                edges[2] = str(int(float(edges[2])))
                f1.write("{}\t{}\t{}\n".format(node_map[edges[0]], node_map[edges[1]], edges[2]))

    def action1_convert_extracted_signed_groups(self, sub):
        # converts numbers to users
        subs = sub.split("_")

        graph = self.import_graph(specific_path=f"graph_data/sentiment_graphs/{subs[0]}_both_{subs[1]}_both.txt")
        s1 = ""
        s2 = ""
        with open("graph_data/sentiment_graphs/extracted_signed_groups/"+sub+".txt", "r") as f:
            first_line = f.readline()
            s1 = first_line.split(",")
            s1.pop()
            second_line = f.readline()
            s2 = second_line.split(",")
            s2.pop()

        nodes = [node for node in graph.nodes]
        s1_users = []
        s2_users = []
        for user in s1:
            s1_users.append(nodes[int(user)])
        for user in s2:
            s2_users.append(nodes[int(user)])

        with open("graph_data/sentiment_graphs/extracted_signed_groups/"+sub+"_names.txt", "w") as f:
            f.write(",".join(s1_users))
            f.write("\n")
            f.write((",".join(s2_users)))


    def test1_save_graphs(self, sub_name, modify):
        filenames = commons.get_filenames_by_subreddit(sub_name, "")
        filenames = ["space_both"]
        for filename in filenames:
            connected_graph = self.get_graph_from_file(filename + ".json", modify)
            if modify:
                filename=filename+"_modified"
            self.export_graph(connected_graph, filename+".txt")

    def test1_save_sentiment_graphs(self, sub_name):
        filenames = commons.all_subreddits
        
        path = "graph_data/"
        for filename in filenames:
            print(filename)
            filename += "_both"
            connected_graph = self.get_graph_from_file(filename + ".json", sentiment=True)
            
            graph = self.aggregate_signed_graph(connected_graph)
            self.export_graph(graph, specific_path=path+"sentiment_graphs/"+filename+".txt")
    
    def test2_save_probability_graphs(self, sub_name):
        
        filenames = commons.get_filenames_by_subreddit(sub_name, "txt")
        for file in filenames:
            graph = self.import_graph(file)
            new_graph = self.aggregate_to_weighted_graph(graph)
            new_graph = self.make_probability_graph(new_graph)
            self.export_graph(new_graph, f"weighted_graphs/{file}")

    def test3_save_signed_graphs(self, sub_name):
        
        filenames = commons.get_filenames_by_subreddit(sub_name, "txt")
        filenames = ["conspiracy0_both_space_both.txt"]
        for file in filenames:
            print(file)
            graph = self.import_graph(specific_path="graph_data/"+file)
            new_graph = self.aggregate_signed_graph(graph)
            self.export_graph(new_graph, specific_path="graph_data/"+f"signed_graphs/{file}")

    def test4_combine_graphs(self, filename1, filename2):
        path = "graph_data/sentiment_graphs/"

        graph1 = self.import_graph(specific_path=path+filename1)
        graph2 = self.import_graph(specific_path=path+filename2)

        merged = self.combine_graphs(graph1, graph2)
        filename1 = filename1.split(".")[0]
        filename2 = filename2.split(".")[0]
        graph_name =  "{}_{}.txt".format(filename1, filename2)
        self.export_graph(merged, specific_path=path+graph_name)


    def test5_save_interweighted_graphs(self, filename1, filename2):
        graph1 = self.import_graph(filename1)
        graph2 = self.import_graph(filename2)
        merged = self.combine_graphs(graph1, graph2)
        print(merged)
        aggregated_graph = self.aggregate_to_weighted_graph(merged)
        probability_graph = self.make_probability_graph(aggregated_graph)

        filename1 = filename1.split(".")[0]
        filename2 = filename2.split(".")[0]
        graph_name =  "{}_{}.txt".format(filename1, filename2)
        self.export_graph(probability_graph, f"weighted_graphs/{graph_name}")

    def test6_combine_signed_graphs(self, filename1, filename2):
        
        filename1 = filename1.split(".")[0]
        filename2 = filename2.split(".")[0]
        graph_name =  "{}_{}.txt".format(filename1, filename2)
        g = self.import_graph(specific_path="graph_data/"+graph_name)
        print(g)
        new_graph = self.aggregate_signed_graph(g)
        self.export_graph(new_graph, f"signed_graphs/{graph_name}")

    def test7_count_edges_across(self, filename1, filename2):
        path = "graph_data/signed_graphs/"
        g1 = nx.read_weighted_edgelist(path+filename1)
        g2 = nx.read_weighted_edgelist(path+filename2)
        g1_nodes = set(g1.nodes)
        g2_nodes = set(g2.nodes)
        filename1 = filename1.split(".")[0]
        filename2 = filename2.split(".")[0]
        merged_graph_name = f"{filename1}_{filename2}.txt"
        g = nx.read_weighted_edgelist(path+merged_graph_name)
        # merged_graph = self.aggregate_signed_graph(merged_graph)
        print(self.count_edges_across(g1_nodes, g2_nodes, g))

    

    def count_positive_edges(self, sub1, sub2, sub):
        path = "graph_data/signed_graphs/"

        graph1 = nx.read_weighted_edgelist(path+sub1)
        group1 = set(graph1.nodes)

        graph2 = nx.read_weighted_edgelist(path+sub2)
        group2 = set(graph2.nodes)


        graph = nx.read_weighted_edgelist(path+sub)

        count_pedges = 0
        print("ok")
        for u,v in graph.edges():
            if (u in group1 and v in group2) or (u in group2 and v in group1):
                
                if graph[u][v]['weight'] == 1:
                    count_pedges += 1
       
        print(count_pedges)

    def count_different_signs(self, filename):
        graph_signed = nx.read_weighted_edgelist(f"graph_data/signed_graphs/{filename}_both.txt")
        graph_sentiment = nx.read_weighted_edgelist(f"graph_data/sentiment_graphs/{filename}_both.txt")
        count = 0

        for u,v in graph_signed.edges():
            if graph_signed[u][v]['weight'] != graph_sentiment[u][v]['weight']:
                count += 1

        print(100*count/len(graph_sentiment.edges))
        return count 




if __name__ == "__main__":
   
    manager = GraphManager()
    modify = False
    sub = "Coronavirus"
    #manager.count_positive_edges("conspiracy0_both.txt", "space_both.txt", "conspiracy0_both_space_both.txt")
    # filename = "conspiracy_both.json"
    
    # manager.test1_save_sentiment_graphs(sub)
    # for sub in commons.all_subreddits:
    # manager.test3_save_signed_graphs("")
    f1 = "conspiracy0_both.txt"
    f2 = "space_both.txt"
    for subs in commons.inter_communities:
        filename = subs[0]+"_"+subs[1]
        print(filename)
        manager.action1_convert_extracted_signed_groups(filename)

    # manager.modify_signed_format("conspiracy0_both_space")
    #     manager.modify_signed_format(sub)
    #f = "Coronavirus_both_science_both.txt"
    #g = manager.import_graph(f)
    #g = manager.aggregate_signed_graph(g)
    #manager.export_graph(g, f"signed_graphs/{f}")
   
    


    # for filename in commons.all_subreddits:
    #     print(filename)
    #     count = manager.count_different_signs(filename)
    
    #     print()
    # manager.test7_count_edges_across(f1, f2)
    # manager.test6_combine_signed_graphs(f1, f2)

    
    # manager.modify_signed_format("conspiracy0_both_space")
    # manager.test7_count_edges_across(f1,f2, "top")
    
    # for comb in combs:
    #    manager.test5_save_interweighted_graphs(comb[0], comb[1])
    # for sub in commons.all_subreddits:
    #     manager.test2_save_probability_graphs(sub)
    # for sub in commons.all_subreddits:
    
    # for sub in commons.all_subreddits:
    #     manager.action1_convert_extracted_signed_groups(sub)
    

    # manager.count_positive_edges("conspiracy0_both.txt", "space_both.txt", "conspiracy0_both_space_both.txt")
       

    
