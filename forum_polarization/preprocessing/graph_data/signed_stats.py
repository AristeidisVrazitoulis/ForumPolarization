import networkx as nx


def count_all_positive_edges(graph):
    count = 1
    for u,v in graph.edges():
        if graph[u][v]['weight'] == 1:
            count += 1
    return count


def count_edges_across_groups(union_graph, s1, s2):
    count_edges = 0
    count_positive_edges = 0

    for u,v in union_graph.edges():
        if (u in s1 and v in s2) or (u in s2 and v in s1):
            count_edges += 1
            if union_graph[u][v]['weight'] == 1:
                count_positive_edges += 1
    
    return (count_edges, count_positive_edges)

def positive_edges_within_group(s_graph):
    count = 0
    for u,v in s_graph.edges():
        if s_graph[u][v]['weight'] == 1:
            #print("ok")
            count += 1
    return count

def compute_intra_stats(graph, s1, s2):
    pe1 = -1
    pe2 = -1
    pea = -1

    s1_graph = graph.subgraph(s1)
    s2_graph = graph.subgraph(s2)
    union_graph = graph.subgraph(s1+s2)
    s1_percentage = 100*(len(s1)/ len(graph.nodes))
    s2_percentage = 100*(len(s2)/ len(graph.nodes))

    positive_edges1 = positive_edges_within_group(s1_graph)
    positive_edges2 = positive_edges_within_group(s2_graph)

    if len(s1_graph.edges) != 0:
        pe1 = 100*(positive_edges1/len(s1_graph.edges))
    
    if len(s2_graph.edges) != 0:
        pe2 = 100*(positive_edges2/len(s2_graph.edges))
    

    (edges_across, positive_edges_across) = count_edges_across_groups(union_graph,s1, s2)
    all_positive_edges = count_all_positive_edges(graph)
    ea = 100*edges_across/len(union_graph.edges)
    if edges_across != 0:
        pea = 100*positive_edges_across/edges_across
    pe = 100*all_positive_edges/len(graph.edges)

    print(f"{s1_percentage:.2f}%\t{s2_percentage:.2f}%\t{pe1:.2f}%\t{pe2:.2f}%\t{ea:.2f}%\t{pea:.2f}%\t{pe:.2f}%")

def compute_inter_stats(graph, s1, s2):

    s1_graph = graph.subgraph(s1)
    s2_graph = graph.subgraph(s2)

    # stats = count_all(graph,s1,s2)
    if len(s1_graph.edges) != 0:
        pe1 = 100*positive_edges_within_group(s1_graph)/len(s1_graph.edges)
    else:pe1 = -1
    if len(s2_graph.edges) != 0:
        pe2 = 100*positive_edges_within_group(s2_graph)/len(s2_graph.edges)
    else:pe2 =-1

    # ea = 100*(stats.count_edges_across/len(graph.edges))
    (ea,pea) = count_edges_across_groups(graph, s1, s2)
    pea = 100*pea/ea
    
    print(f"{pe1:.2f}%\t{pe2:.2f}%\t{pea:.2f}%")


def get_intra_groups(full_path):
    with open(full_path, "r") as f:
        first_line = f.readline()
        s1 = first_line.split(",")
        s1.pop()
        second_line = f.readline()
        s2 = second_line.split(",")
        s2.pop()
    return (s1,s2)



def get_inter_groups(filename):
    names = filename.split("_")
    community1 = nx.read_weighted_edgelist("sentiment_graphs/"+names[0]+"_both.txt")
    community2 = nx.read_weighted_edgelist("sentiment_graphs/"+names[1]+"_both.txt")
    return (list(community1.nodes), list(community2.nodes))



# it counts the relationship of the groups made in the random_eigensign algorithm and the groups of the subreddits communities
def count_relation(c1,c2,s1,s2):
    common_users = c1.intersection(c2)
    c1 = c1.difference(common_users)
    c2 = c2.difference(common_users)

    # S1
    s1_count = [0,0,0]
    for user in s1:
        if user in c1:
            s1_count[0] += 1
        elif user in c2:
            s1_count[1] += 1
        else:
            s1_count[2] += 1
    print("S1")
    print("A\tB\tCM")
    print(f"{s1_count[0]/len(s1):.2f}\t{s1_count[1]/len(s1):.2f}\t{s1_count[2]/len(s1):.2f}")

    # S1
    s2_count = [0,0,0]
    for user in s2:
        if user in c1:
            s2_count[0] += 1
        elif user in c2:
            s2_count[1] += 1
        else:
            s2_count[2] += 1
    print("S2")
    print("A\tB\tCM")
    print(f"{s2_count[0]/len(s2):.2f}\t{s2_count[1]/len(s2):.2f}\t{s2_count[2]/len(s2):.2f}")






def run_intra_stats(path):
    filenames = ["Coronavirus","conspiracy", "science", "WitchesVsPatriarchy", "MensRights", "lgbt", "Conservative", "conspiracy0","space"]
    filenames = ["Coronavirus_conspiracy","science_conspiracy","WitchesVsPatriarchy_MensRights","lgbt_Conservative", "conspiracy0_space"]
    print("|S1|\t|S2|\tPE1\tPE2\tEA\tPEA\tPE")
    for filename in filenames:
        #filename += ".txt"
        full_name = path+"extracted_signed_groups/"+filename
        s1,s2 = get_intra_groups(full_name+"_names.txt")
        print(filename)
        parts = filename.split("_")
        graph = nx.read_weighted_edgelist(f"{path}{parts[0]}_both_{parts[1]}_both.txt")

        # graph = nx.read_weighted_edgelist(path+filename+"_both.txt")

        compute_intra_stats(graph, s1, s2)

def run_inter_stats():
    filenames = ["Coronavirus_conspiracy","science_conspiracy","WitchesVsPatriarchy_MensRights","lgbt_Conservative", "conspiracy0_space"]
    print("PE1\tPE2\tPEA")
    for filename in filenames:
        #filename += ".txt"
        s1,s2 = get_inter_groups(filename)
        print(filename)
        parts = filename.split("_")
        graph = nx.read_weighted_edgelist("sentiment_graphs/"+parts[0]+"_both_"+parts[1]+"_both.txt")
        compute_inter_stats(graph, s1, s2)

def get_relation():
    filenames = ["Coronavirus_conspiracy","science_conspiracy","WitchesVsPatriarchy_MensRights","lgbt_Conservative", "conspiracy0_space"]
    for filename in filenames:
        print(filename)
        names = filename.split("_")
        g1 = nx.read_weighted_edgelist("sentiment_graphs/"+names[0]+"_both.txt")
        g2 = nx.read_weighted_edgelist("sentiment_graphs/"+names[1]+"_both.txt")
        c1 = set(g1.nodes)
        c2 = set(g2.nodes)


        s1,s2 = get_intra_groups("sentiment_graphs/extracted_signed_groups/"+filename+"_names.txt")
        count_relation(c1,c2,set(s1),set(s2))
        print()





# run_intra_stats("sentiment_graphs/")
# run_inter_stats()
get_relation()
#print("PE1\tPE2\tPEA")

# filenames = ["conspiracy0_space"]






