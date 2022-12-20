import sys
import networkx as nx

args = sys.argv


subs = ["Coronavirus", "science", "conspiracy", "worldnews", "WitchesVsPatriarchy", "MensRights"]
cats = ["both"]


# print(node_map)
for sub in subs:
    for cat in cats:
        filename = "WitchesVsPatriarchy_both_MensRights_both.txt"
        graph = nx.read_weighted_edgelist(filename)

        nodes = list(graph.nodes)
        n_edges = len(graph.edges)
        node_map = {}

        node_map = {nodes[i]:i for i in range(len(nodes))}
        path = "modified_format/"+filename
        with open(path, 'w') as f1, open(filename, 'r') as f2:
            f1.write("#\t{}\n".format(n_edges))
            for line in f2.readlines():
                edges = line.split()
                f1.write("{}\t{}\t{}\n".format(node_map[edges[0]], node_map[edges[1]], edges[2]))
        break
    