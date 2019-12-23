"""
Some helper functions to handle the math/methods
"""
import os
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

FIGURE_SIZE = (12, 7)
STYLES = ["^b-", "*r-", "om-"]


def column(vector):
    """
    Recast 1d array into into a column vector, suitable for lin. algebra operations
    """
    vector = np.array(vector)
    return vector.reshape(len(vector), 1)


def get_unique_ids(length):
    # Using MATLAB indexing for now
    return [str(_id) for _id in range(1, length + 1)]


def graph_plot(adj):
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
    plt.show()


def line_plot(y_values_list, x_values, title=None, ylabel=None, xlabel=None, labels=None, ylim=None):
    """
    :param y_values_list: list(list())
    :param x_values: list()
    :param title: str
    :param ylabel: str
    :param xlabel: str
    :param labels: list(str)
    :param ylim: float
    """
    plt.rcParams["figure.figsize"] = FIGURE_SIZE
    for i, y_values in enumerate(y_values_list):
        plt.plot(x_values, y_values, STYLES[i], label=labels[i])

    plt.title(title) if title else None
    plt.xlabel(xlabel) if xlabel else None
    plt.ylabel(ylabel) if ylabel else None
    plt.ylim(0, ylim) if ylim else None
    plt.legend(loc='lower right')
    plt.show()
