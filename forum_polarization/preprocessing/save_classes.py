from graph_manager import GraphManager

import random

manager = GraphManager()
theme = "WitchesVsPatriarchy_controversial_MensRights_controversial"

def save_classes(theme):
    parts = theme.split("_")
    filename1 = parts[0]+"_"+parts[1]+".txt"
    filename2 = parts[2]+"_"+parts[3]+".txt"
    print("arrived")
    print(filename1,filename2)
    G1 = manager.import_graph(filename1)
    G2 = manager.import_graph(filename2)
    

    groupA = set(G1.nodes)
    groupB = set(G2.nodes)

    mutual_nodes = groupA.intersection(groupB)

    for node in mutual_nodes:
        if random.random() > 0.5:
            groupA.remove(node)
        else:
            groupB.remove(node)
    save_file = "/gephi_format/"+theme+"_classes.csv"
    
    with open(save_file, "w") as f:
        f.write("Id,Class\n")
        for node in groupA:
            f.write(f"{node},0\n")
        for node in groupB:
            f.write(f"{node},1\n")
    

save = 1
if save:
    save_classes(theme)