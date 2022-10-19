# script to do a random walk on a graph, starting from a random node of a given side and counting the number of *times* we end up in either a node from the same side or from the other side
# random walk type3.

# algorithm implemented by https://github.com/gvrkiran/controversy-detection
# code/randomwalk/computePolarizationScoreRandomwalk.py
# here is a refactored version of that script

import random,sys
from operator import itemgetter
from graph_manager import GraphManager
from networkx.algorithms import community

# constants of the array that saves the stats of the experiment
LEFT_LEFT = 0
LEFT_RIGHT = 1
RIGHT_LEFT = 2
RIGHT_RIGHT = 3

class RandomWalkSimulation:
	
	def __init__(self, graph, sample_percent, n_experiments):
		# NetworkX Graph
		self.G = graph
		self.sample_percent = sample_percent
		self.n_experiments = n_experiments
		# try metis
		self.groupA, self.groupB = community.kernighan_lin_bisection(self.G)
		self.count_stats = [0 for i in range(4)]
		self.p = [0 for i in range(4)]
		self.map_functions = {True:self.getNodesFromLabelsWithHighestDegree, False:self.getRandomNodesFromLabels}

	# parameter k = number of random nodes to generate
	def getRandomNodes(self, k):
		nodes = self.G.nodes()
		random_nodes = {}
		for i in range(k):
			random_num = random.randint(0,len(nodes)-1)
			random_nodes[nodes[random_num]] = 1
		return random_nodes

	# parameter k = no. of random nodes to generate, flag could be "left", "right" or "both". If both, k/2 from one side and k/2 from the other side are generated.
	def getRandomNodesFromLabels(self, k, group): 
		random_nodes = []
		for i in range(k):
			random_num = random.randint(0,len(group)-1)
			random_nodes.append(group[random_num])
		
		random_nodes_map = {elem : 1 for elem in random_nodes}
		return random_nodes_map

	# first take the nodes with the highest degree according to the "flag" and then take the top k
	def getNodesFromLabelsWithHighestDegree(self, k, group_dict): 
		random_nodes = {}
		dict_degrees = { node : self.G.degree(node) for node in self.G.nodes() }

		# sorts nodes by degrees
		sorted_dict = sorted(dict_degrees.items(), key=itemgetter(1), reverse=True) 
		
		count = 0
		for node in sorted_dict:
			if count>k:
				break
			if not node[0] in group_dict:
				continue
			random_nodes[node[0]] = node[1]
			count += 1

		return random_nodes

	# returns if we ended up in a "left" node or a "right" node
	def performRandomWalk(self, starting_node,user_nodes_side1,user_nodes_side2): 
		# contains unique nodes seen till now
		dict_nodes = {} 
		
		step_count = 0
		side = ""

		while(True):
			# print "starting from ", starting_node, "num nodes visited ", len(dict_nodes.keys()), " out of ", len(nodes)
			neighbors = list(self.G.neighbors(starting_node))
			random_num = random.randint(0, len(neighbors)-1)
			starting_node = neighbors[random_num]
			dict_nodes[starting_node] = 1
			step_count += 1
			if starting_node in user_nodes_side1:
				side = "left"
				break
			if starting_node in user_nodes_side2:
				side = "right"
				break

		return side

	# returns the number of steps taken before reaching *ALL* node from the set of user nodes. difference from the above method is that we should reach all nodes, instead of just any one of them.
	def performRandomWalkFull(self, starting_node, user_nodes): 
		dict_nodes = {} # contains unique nodes seen till now
		num_edges = len(self.G.edges())
		step_count = 0
		total_other_nodes = len(user_nodes.keys())
		dict_already_seen_nodes = {}
		flag = 0

		while(flag!=1):
			# print "starting from ", starting_node, "num nodes visited ", len(dict_nodes.keys()), " out of ", len(nodes)
			neighbors = self.G.neighbors(starting_node)
			random_num = random.randint(0,len(neighbors)-1)
			starting_node = neighbors[random_num]
			dict_nodes[starting_node] = 1
			step_count += 1
			if(user_nodes.has_key(starting_node)):
				dict_already_seen_nodes[starting_node] = 1
				print( sys.stderr, "seen nodes ", len(dict_already_seen_nodes.keys()))
				if(len(dict_already_seen_nodes.keys())==total_other_nodes):
					flag = 1
			if(step_count>num_edges**2): # if stuck
				break
			if(step_count%100000==0):
				print(sys.stderr, step_count, "steps reached")
		return step_count
	
	

	def perform_single_random_walk_experiment(self, user_nodes1, user_nodes2, is_left=True):
		endup_left = 0
		endup_right = 0

		user_nodes_list = list(user_nodes1.keys())
		for i in range(len(user_nodes_list)-1):
			node = user_nodes_list[i]
			other_nodes = user_nodes_list[:i] + user_nodes_list[i+1:]
			other_nodes_dict = {node:1 for node in other_nodes}
			if is_left:
				side = self.performRandomWalk(node,other_nodes_dict,user_nodes2)
			else: side = self.performRandomWalk(node,user_nodes2, other_nodes_dict)

			if side=="left":
				endup_left += 1
			elif side=="right":
				endup_right += 1

		return (endup_left, endup_right)

	# starts and performs the whole random walk algorithm and returns the stats for each case
	# The variables direction1_direction2 count the times that we performed rw starting from destination1 and ended up on destination2
	def perform_random_walk_experiments(self, choose_highest_degree=True):
		self.is_highest_degree = choose_highest_degree
		left = list(self.groupA)
		dict_left = {node_name:1 for node_name in left}

		right = list(self.groupB)
		dict_right = {node_name:1 for node_name in right}

		# also assume that you are given a set of nodes (news articles) that have been read by a user
		# user_nodes = getRandomNodes(G,2) # for now, using a random set of nodes. Use a specific set later when testing
		# start_end

		left_percent = int(self.sample_percent*len(dict_left.keys()))
		right_percent = int(self.sample_percent*len(dict_right.keys()))

		for i in range(self.n_experiments):

			user_nodes_left = self.map_functions[choose_highest_degree](left_percent, left)
			user_nodes_right = self.map_functions[choose_highest_degree](right_percent, right)

			# print "randomly selected user nodes ", user_nodes
			(endup_left, endup_right) = self.perform_single_random_walk_experiment(user_nodes_left, user_nodes_right)
			self.count_stats[LEFT_LEFT] += endup_left
			self.count_stats[LEFT_RIGHT] += endup_right

			(endup_left, endup_right) = self.perform_single_random_walk_experiment(user_nodes_right, user_nodes_left, False)
			self.count_stats[RIGHT_LEFT] += endup_left
			self.count_stats[RIGHT_RIGHT] += endup_right
				
			print("experiment:", i)
		

	# fills the array p of probabilities
	def compute_probabilities_by_stats(self):
		self.p[0] = round(self.count_stats[LEFT_LEFT]*1.0/(self.count_stats[LEFT_LEFT]+self.count_stats[RIGHT_LEFT]),4)
		self.p[1] = round(self.count_stats[LEFT_RIGHT]*1.0/(self.count_stats[LEFT_RIGHT]+self.count_stats[RIGHT_RIGHT]),4)
		self.p[2] = round(self.count_stats[RIGHT_LEFT]*1.0/(self.count_stats[LEFT_LEFT]+self.count_stats[RIGHT_LEFT]),4)
		self.p[3] = round(self.count_stats[RIGHT_RIGHT]*1.0/(self.count_stats[LEFT_RIGHT]+self.count_stats[RIGHT_RIGHT]),4)


	# takes as an input vector p of length 4
	# p[0] = Pxx, p[1] = Pxy, p[2] = Pyx, p[3] = Pyy
	def compute_polarity(self, p):
		p_xx = p[0]
		p_xy = p[1]
		p_yx = p[2]
		p_yy = p[3]
		return p_xx*p_yy - p_xy*p_yx


	def easy_run(self, highest_degree=True):
		self.perform_random_walk_experiments(highest_degree)
		self.compute_probabilities_by_stats()
		self.polarity = self.compute_polarity(self.p)
		self.print_all_stats()
		print("polarity:",self.polarity)

	def print_all_stats(self):
		print("--------------------------------------")
		print("left -> left", self.count_stats[LEFT_LEFT], "p_xx =",self.p[0])
		print("left -> right", self.count_stats[LEFT_RIGHT], "p_xy =",self.p[1])
		print("right -> right", self.count_stats[RIGHT_LEFT], "p_yx =",self.p[2])
		print("right -> left", self.count_stats[RIGHT_RIGHT], "p_yy =",self.p[3])
	
	# saves stats to file
	def save_stats(self, graph_filename):
		data_line = "{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
			graph_filename,self.n_experiments,self.sample_percent,
			self.count_stats[LEFT_LEFT],
			self.count_stats[LEFT_RIGHT],
			self.count_stats[RIGHT_LEFT],
			self.count_stats[RIGHT_RIGHT],
			self.p[0],self.p[1],self.p[2],self.p[3],
			self.polarity,
			self.is_highest_degree
			)
		with open("statistics/rw_stats.csv","a") as f:
			f.write(data_line)


# side = sys.argv[2] # left, right or both

# G = nx.read_weighted_edgelist('news_news_matrix_largest_CC.txt',delimiter=',')
# G = nx.read_weighted_edgelist('political_blogs_largest_CC.txt',delimiter=',')

if __name__ == "__main__":

	manager = GraphManager()
	filename = "merged.txt"
	G = manager.import_graph(filename)
	sample_percent = 1
	n_experiments = 50
	select_highest_degree = True
	save_stat = False
	rw = RandomWalkSimulation(G, sample_percent, n_experiments)
	rw.easy_run(select_highest_degree)

	if save_stat:
		rw.save_stats(filename)




	






