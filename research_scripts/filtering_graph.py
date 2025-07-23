import pandas as pd
import igraph as ig
import project_config


def filter_graph(graph, drug_ids, actual_relations):
    """
    Filters the input graph based on the specified target nodes and actual relations.
    """
    # Keep only edges that match the actual relations
    kept_edges = graph.es.select(lambda e: e["relation"] in actual_relations)
    filtered_graph = graph.subgraph_edges(kept_edges, delete_vertices=False)

    # Find nodes related to the target nodes
    target_indices = [v.index for v in filtered_graph.vs if v["name"] in drug_ids]
    related_nodes = set(target_indices)

    # Include neighbors of target nodes
    for idx in target_indices:
        related_nodes.update(
            filtered_graph.neighbors(idx, mode="all")
        )  #"out" or "in" can be used here 

    subg = filtered_graph.induced_subgraph(list(related_nodes))
    return subg
