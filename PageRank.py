####################################################################
# The code in this project was collaboratively written by:         #
# Magnus Simoni Jahn, Frida Nøhr Laustsen and Marie Haahr Petersen #
####################################################################

import networkx as nx
from random import choice
from random import random
from collections import Counter
from timeit import default_timer

filenames = ["bigRandom", "medium", "p2p-Gnutella08-mod", "test", "three", "tiny", "wikipedia"]

def load_graph(filename):
    """
    Function:       Loads txt file with edges and converts it to a graph.

    Input:          txt file.

    Output:         networkx DiGraph.
    """
    with open(filename, "r") as f:
        next(f)
        edges = list()
        for lines in f:
            line = lines.strip().split()
            edges.append(tuple(line))
        G = nx.DiGraph(edges)
        return G

def dangling_nodes(graph):
    """
    Function:       Checks for dangling nodes in graph.

    Input:          networkx DiGraph.

    Output:         Set of dangling nodes.
    """
    notdangling = set()
    for edge in graph.edges():
        notdangling.add(edge[0])
    dangling = list()
    for node in graph.nodes():
        if node not in notdangling:
            dangling.append(node)
    return dangling

def node_counter(graph):
    """
    Function:       Creates a dictionary to keep track of visited notes (dict[node]: visits).

    Input:          networkx DiGraph.

    Output:         Dictionary with nodes as keys and visits as values (starting at 0).
    """
    node_count = dict()
    for node in graph.nodes():
        node_count[node] = 0
    return node_count

def random_surfer(graph, iterations, damping):
    """
    Function:       Ranks most visited nodes in graph by surfing graph, occasionally jumping to random node.

    Input:          networkx DiGraph.

    Output:         Dictionary with nodes as keys and number of visits as values.
    """
    m = damping
    node_count = node_counter(graph)    # Counter to keep track of visited notes.
    nodes = list()                      # List with all nodes in graph.
    for node in graph.nodes():
        nodes.append(node)
    curr_node = choice(nodes)           # Picks random node to begin the surf.
    
    curr_iteration = 0

    while curr_iteration < iterations:  # Loop stops when curr_iteration is equal to the desired amount of iterations.
        node_count[curr_node] += 1      # Adds 1 to the number of visits
        if len(list(graph.neighbors(curr_node))) != 0 and (random() < m): 
                                        # Picks neighbor if they exists and damping doesnt kick in.
            curr_node = choice(list(graph.neighbors(curr_node)))
        else:
            curr_node = choice(nodes)   # Picks random node in network as next node.
        curr_iteration += 1
    return node_count

def page_rank(graph, n, damping):
    """
    Function:   Ranks nodes in a graph by weighing importance of nodes linking to and from each node.

    Input:      networkx DiGraph, iterations(n), damping factor (between 0 and 1).

    Output:     Dictionary with notes as keys and importance score as values.
    """
    m = damping
    graph_size = len(graph)             # Size of the graph.
    reverse = nx.reverse(graph)         # Reversed graph used to find backlinks.
    dangling = dangling_nodes(graph)    # Dangling nodes.
    x = dict()                          # xk dictionary with node as key and initially 1/graph_size as value.
    for node in graph.nodes():
        x[node] = 1/graph_size
    mS = (1 - m) * 1/graph_size         # Because matrix S * xk = xk ==> mS has m/n in all entries.

    for _ in range(n):                  # Outerloop iterating n times, updating D each iteration.
        D = 0                           # Only computed once per outer loop, since all rows in D are the same.
        for d_node in dangling:
            D += x[d_node]/graph_size
        D = D * m

        for node, importance in x.items():
            backlinks = list()          # Using the reversed graph to identify backlinks to node.
            for backlink in reverse.neighbors(node):
                backlinks.append(backlink)

            votes = list()              # Now computing vote size to node from each backlink.
            for b_node in backlinks:
                votes.append(1/len(list(graph.neighbors(b_node)))) 
                                        # Adding 1/outlinks to votes for each backlink to node.

            A = 0
            for i, b_node in enumerate(backlinks): 
                                        # Computing matrix A.
                A = A + votes[i] * x[b_node] 
                                        # Adding each backlinks contribution to A based on votesplit and importance.
            A *= m 
            x[node] = A + D + mS        # Updating importance score for node.
    return x

def main():
    G = load_graph("data/"+filenames[2]+".txt") 
                                        # Loads Gnutella graph.
    timer = default_timer()
    print("Running Random surfer algorithm... ")
    surf = random_surfer(G, 100_000_000, 0.85) 
                                        # Surfs G with 100.000.000 iterations and damping factor = 0.85.
    print(f"Done. Time cost: {round(default_timer() - timer, 2)} s\n")                           

    timer = default_timer()
    print("Running PageRank algorithm... ")
    rank = page_rank(G, 200, 0.85)      # Ranks pages with 100 iterations and damping factor = 0.85. 
    print(f"Done. Time cost: {round(default_timer() - timer, 2)} s\n")               
    
    print("Most visited notes by Random surfer algorithm (rank, node, visits): ")
    top_surf = enumerate(Counter(surf).most_common(10), 1)
    for i, node in top_surf:            # Prints each node along with the amount of visits.
        print(i, node)

    print("\nMost important nodes ranked by PageRank algorithm (rank, node, importance score): ")
    top_rank = enumerate(Counter(rank).most_common(10), 1) 
    for i, node in top_rank:            # Prints each node along with its importance score.
        print(i, (node[0], round(node[1], 7)))

if __name__ == "__main__":
	main()