from graph_manager import GraphManager
import networkx as nx

def calculate_average_degree(G):
    return sum([node[1] for node in G.degree])/len(G.degree)


subs = ["Coronavirus", "science", "conspiracy", "worldnews", "WitchesVsPatriarchy", "MensRights"]
cats = ["top","controversial","both"]
manager = GraphManager()

for sub in subs:
    for cat in cats:
        filename = f"{sub}_{cat}.txt"
        G = manager.import_graph(filename)
        print(len(G.edges))
        G = nx.Graph(G)

        print(G)
        print()

