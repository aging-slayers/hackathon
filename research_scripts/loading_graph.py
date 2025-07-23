import pandas as pd
import igraph as ig
import project_config

def build_igraph_from_triplets(triplets):
    # Collecting unique nodes
    nodes = sorted(set([s for s, _, _ in triplets] + [t for _, _, t in triplets]))
    node2id = {node: i for i, node in enumerate(nodes)}

    # Forming edges and relations
    edges = [(node2id[s], node2id[t]) for s, _, t in triplets]
    relations = [p for _, p, _ in triplets]

    # Building the graph
    g = ig.Graph(directed=True)
    g.add_vertices(nodes) 
    g.add_edges(edges)
    g.es['relation'] = relations

    return g


def loading_graph(path_graph: str):
    if not path_graph:
        path_graph = project_config.PATH_DRKG
    # Load the DRKG dataset
    drkg = pd.read_csv(path_graph, sep="\t", header=None)
    triplets = drkg.values.tolist()

    g = build_igraph_from_triplets(triplets)

    g.write(project_config.PATH_GRAPH, format="gml")
    pass
