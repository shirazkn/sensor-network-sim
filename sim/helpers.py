"""
Some helper functions to handle the math/methods
"""
import os
import networkx as nx
from matplotlib.pyplot import show as plt_show


def column(vector):
    """
    Recast 1d array into into a column vector, suitable for lin. algebra operations
    """
    return vector.reshape(len(vector), 1)


def get_unique_ids(length):
    # TODO - use random Hex labels for sensors?
    # Using MATLAB indexing for now
    return [str(_id) for _id in range(1, length + 1)]


def show_graph(adj):
    """
    Visualize a graph using networkx library
    :param adj: Adjacency matrix of the graph
    """
    n_nodes = len(adj[0])
    graph = nx.Graph()
    nodes = get_unique_ids(n_nodes)
    for i in range(n_nodes):
        for j in range(i+1, n_nodes):
            if adj[i][j]:
                graph.add_edge(nodes[i], nodes[j])

    nx.draw_networkx(graph, with_labels=True, node_color=[[0.7, 0.8, 0.2]])
    plt_show()
