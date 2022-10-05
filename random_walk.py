from graph_manager import GraphManager
from networkx.algorithms import community

import networkx as nx
import random

manager = GraphManager()
filename = "merged_graph.txt"
multi_graph = manager.import_graph(filename)
graph = nx.Graph(multi_graph)

# note: if it is a Directed Graph we focus on the IN degree

# graph partitioning
groupA, groupB = community.kernighan_lin_bisection(graph)

subgraphA = graph.subgraph(groupA)


def get_starting_node_from_group(group_name):
    random_node = ""
    if group_name == "groupA":
        random_node = random.choice(tuple(groupA))
    else:
        random_node = random.choice(tuple(groupB))
    
    return random_node


def determine_node_group(node_name):
    return "groupA" if node_name in groupA else "groupB"

def random_walk(graph, starting_node, walk_limit=100):
   
    random_node = starting_node
    #Traversing through the neighbors of start node
    for i in range(walk_limit):
        list_for_nodes = list(graph.neighbors(random_node))
        
        # choose a node randomly from neighbors
        if len(list_for_nodes)!=0:
            random_node = random.choice(list_for_nodes) 
        # if random_node having no outgoing edges
        else:
            random_node = random.choice([i for i in range(graph.number_of_nodes())])

    return random_node

def perform_rw_starting_from_group(group_name, times):
    local_times = 5
    same_group_count = 0
    for i in range(times):
        starting_node = get_starting_node_from_group(group_name)
        for j in range(local_times):
            ending_node = random_walk(graph, starting_node, 500)
            if determine_node_group(ending_node) == group_name:
                same_group_count += 1
    
    return same_group_count
            



count = perform_rw_starting_from_group("groupA", 100)
print(count)
print(500)
        








