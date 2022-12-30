from graph_manager import GraphManager
import networkx as nx
import pandas as pd
def calculate_average_degree(G):
    return sum([node[1] for node in G.degree])/len(G.degree)


subs = ["Coronavirus", "science", "conspiracy", "worldnews", "WitchesVsPatriarchy", "MensRights"]
cats = ["top","controversial","both"]
manager = GraphManager()


filename = "Coronavirus_both.txt"
G = manager.import_graph(filename)
print(G)
G = nx.Graph(G)
print(G)
