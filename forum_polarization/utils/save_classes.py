from preprocessing.graph_manager import GraphManager
from algorithms.random_walk import RandomWalkSimulation
import random
import networkx as nx

manager = GraphManager()
theme = "lgbt_top_Conservative_top"
path = f"../preprocessing/graph_data/"

def save_intra_classes(theme):
    
    graph = nx.read_weighted_edgelist(path+f"{theme}.txt")
    rw = RandomWalkSimulation(graph)
    rw.bisect_metis()
    groupA = rw.groupA
    groupB = rw.groupB
    save_file_path = path+"gephi_format/"+f"{theme}_classes.csv"
    save_to_file(save_file_path, groupA, groupB)

def save_to_file(save_file_path, groupA, groupB):
    with open(save_file_path, "w") as f:
        f.write("Id,Class\n")
        for node in groupA:
            f.write(f"{node},0\n")
        for node in groupB:
            f.write(f"{node},1\n")


def save_inter_classes(theme):
    parts = theme.split("_")
    filename1 = parts[0]+"_"+parts[1]+".txt"
    filename2 = parts[2]+"_"+parts[3]+".txt"
    print("arrived")
    print(filename1, filename2)
    G1 = nx.read_weighted_edgelist(path+filename1)
    G2 = nx.read_weighted_edgelist(path+filename2)
    

    groupA = set(G1.nodes)
    groupB = set(G2.nodes)

    mutual_nodes = groupA.intersection(groupB)

    for node in mutual_nodes:
        if random.random() > 0.5:
            groupA.remove(node)
        else:
            groupB.remove(node)
    save_file = path+"gephi_format/"+theme+"_classes.csv"
    save_to_file(save_file, groupA, groupB)
    
    
    

save = 1
if save:
    save_inter_classes(theme)