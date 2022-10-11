from graph_manager import GraphManager
from networkx.algorithms import community
from networkx.algorithms import edge_betweenness_centrality

# import networkx as nx
import random
class RandomWalkPolarity:

    def __init__(self, graph):
        self.graph = graph
        # graph partitioning
        self.groupA, self.groupB = community.kernighan_lin_bisection(graph)
        # total amount of experiments
        self.n_experiments = 3000
        # max steps
        self.walk_limit = 5
        # the amount of times we conduct the experiment from the same starting node
        self.local_times = 2


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

    def perform_rw_starting_from_group(self, starting_group_name):
        
        same_group_count = 0
        for i in range(self.n_experiments):
            starting_node = self.get_starting_node_from_group(starting_group_name)
            for j in range(self.local_times):
                ending_node = self.random_walk(starting_node, self.walk_limit)
                # if the starting and the ending group is the same
                if self.determine_node_group(ending_node) == starting_group_name:
                    same_group_count += 1
        
        return same_group_count

    def calculate_probs_from_group(self, starting_group):
        total = self.n_experiments*self.local_times
        countXX = self.perform_rw_starting_from_group(starting_group)
        countXY = total - countXX

        probXX = countXX/total
        probXY = countXY/total

        return (probXX, probXY)

    def measure_polarity(self,pxx,pyy,pxy,pyx):
        return pxx*pyy-pxy*pyx

        
            

if __name__ == "__main__":

    manager = GraphManager()
    filename = "sample_graph.txt"
    multi_graph = manager.import_graph(filename)
    
    print(len(multi_graph))
    

    # graph = nx.Graph(multi_graph)
    # graph.remove_node("AutoModerator")
    # rw = RandomWalkPolarity(multi_graph)
    
    # probXX,probXY = rw.calculate_probs_from_group("groupA")
        
    # probYY,probYX = rw.calculate_probs_from_group("groupB")

    # polarity = rw.measure_polarity(probXX,probYY,probXY,probYX)
    
    print("Ok")
    # edge_betweenness_centrality(multi_graph)
    print("DONEEE")
    # print(polarity)
        








