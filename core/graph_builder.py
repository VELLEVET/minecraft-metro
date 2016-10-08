"""
Graph builder module.

Builds stations and crosses graph.
"""


import networkx as nx
import matplotlib.pyplot as plot


def build_graph(stations_and_crosses: dict):
    """
    Build stations and crosses graph
    :param stations_and_crosses: Stations and crosses dict
    :return: Resulting graph
    """

    graph = nx.Graph()

    for id, station in stations_and_crosses['stations'].items():
        graph.add_node(id)

    for id, cross in stations_and_crosses['crosses'].items():
        graph.add_node(id)

    for id, cross in stations_and_crosses['crosses'].items():
        for d, conn in cross['connections'].items():
            graph.add_edge(id, conn['id'])

    return graph


def draw(stations_and_crosses:dict, graph: nx.Graph):
    """
    Draw and show graph

    :param stations_and_crosses: Stations and crosses dict
    :param graph: Graph
    """

    pos = dict()
    st_dirs = dict()
    labels = dict()
    stations = list()
    crosses = list()

    for id, cross in stations_and_crosses['crosses'].items():
        for d, conn in cross['connections'].items():
            if conn['type'] == 's':
                st_dirs[conn['id']] = d
        pos[id] = (cross['x'], -cross['z'])
        labels[id] = id
        crosses.append(id)

    for id, station in stations_and_crosses['stations'].items():
        x = stations_and_crosses['crosses'][station['cross_id']]['x']
        y = -stations_and_crosses['crosses'][station['cross_id']]['z']

        x += {'n': 0, 's': 0, 'w': -200, 'e': 200}[st_dirs[id]]
        y += {'n': 200, 's': -200, 'w': 0, 'e': 0}[st_dirs[id]]

        pos[id] = (x, y)
        labels[id] = id
        stations.append(id)

    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_nodes(graph, pos, nodelist=stations, node_color='#ffffff', node_size=300, node_shape='o')
    nx.draw_networkx_nodes(graph, pos, nodelist=crosses, node_color='#00ff00', node_size=300, node_shape='s')
    nx.draw_networkx_labels(graph, pos, labels, font_size=11)

    plot.axis('off')
    plot.show()


def find_paths(graph: nx.Graph):
    """
    Finds shortest paths between all nodes in given graph

    :param graph: Graph
    :return: Shortest paths
    """

    return nx.shortest_path(graph)
