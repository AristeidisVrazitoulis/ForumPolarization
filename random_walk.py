from graph_manager import GraphManager
from networkx.algorithms import community

import networkx as nx
import random

class RandomWalkPolarity:

    def __init__(self, graph):
        self.graph = graph
        # graph partitioning
        self.groupA, self.groupB = community.kernighan_lin_bisection(graph)

        self.local_times = 5
        self.walk_limit = 250



    def get_starting_node_from_group(self, group_name):
        random_node = ""
        if group_name == "groupA":
            random_node = random.choice(tuple(self.groupA))
        else:
            random_node = random.choice(tuple(self.groupB))
        
        return random_node


    def determine_node_group(self, node_name):
        return "groupA" if node_name in self.groupA else "groupB"

    def random_walk(self, starting_node, walk_limit=100):
    
        random_node = starting_node
        #Traversing through the neighbors of start node
        for i in range(walk_limit):
            list_for_nodes = list(self.graph.neighbors(random_node))
            
            # choose a node randomly from neighbors
            if len(list_for_nodes)!=0:
                random_node = random.choice(list_for_nodes) 
            # if random_node having no outgoing edges
            else:
                random_node = random.choice([i for i in range(self.graph.number_of_nodes())])

        return random_node

    def perform_rw_starting_from_group(self, group_name, n_experiments):
        
        same_group_count = 0
        for i in range(n_experiments):
            starting_node = self.get_starting_node_from_group(group_name)
            for j in range(self.local_times):
                ending_node = self.random_walk(starting_node, self.walk_limit)
                if self.determine_node_group(ending_node) == group_name:
                    same_group_count += 1
        
        return same_group_count
            

if __name__ == "__main__":

    manager = GraphManager()
    filename = "conspiracy_unified.txt"
    multi_graph = manager.import_graph(filename)
    
    graph = nx.Graph(multi_graph)
    rw = RandomWalkPolarity(graph)
    n_experiments = 500
    total = n_experiments*rw.local_times
    print(total)
    countXX = rw.perform_rw_starting_from_group("groupA", n_experiments)
    countXY = total - countXX

    probXX = countXX/total
    probXY = countXY/total
    
    countYY = rw.perform_rw_starting_from_group("groupB", n_experiments)
    countYX = total - countYY

    probYY = countYY/total
    probYX = countYX/total


    
    print(countXX)
    print(countXY)
    print()
    print(countYY)
    print(countYX)

    s = probXX*probYY - probYX*probXY
    print(s)
        








