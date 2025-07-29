import networkx as nx


def neighborhood(G, node, n):
    # TODO do something simpler if n = 1
    path_lengths = nx.single_source_dijkstra_path_length(G, node)
    return [node for node, length in path_lengths.items() if length == n]
