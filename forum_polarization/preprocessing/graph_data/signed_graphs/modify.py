import pathlib
import sys
p = pathlib.Path(__file__).parents[3]

p1 = str(p)
sys.path.insert(1, p1)

import networkx as nx
from utils import commons



print(pathlib.Path().resolve())
print(pathlib.Path(__file__).parent.resolve())
print("ok")
subs = ["abortion", "TwoXChromosomes"]
# print(subs)#
# print(node_map)
path = "forum_polarization/preprocessing/graph_data/signed_graphs/"
for sub in subs:

        filename = f"{sub}_both.txt"
        full = path+filename
        graph = nx.read_weighted_edgelist(full)

        nodes = list(graph.nodes)
        n_edges = len(graph.edges)
        node_map = {}

        node_map = {nodes[i]:i for i in range(len(nodes))}
        
        with open(f"{path}{sub}.txt", 'w') as f1, open(full, 'r') as f2:
            f1.write("#\t{}\n".format(n_edges))
            for line in f2.readlines():
                edges = line.split()
                f1.write("{}\t{}\t{}\n".format(node_map[edges[0]], node_map[edges[1]], str(int(float(edges[2])))))
        
    