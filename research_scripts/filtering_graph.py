def filter_graph(graph, drug_ids):
    """
    Filters the input graph based on the specified target nodes.
    """
    # Find nodes related to the target nodes
    target_indices = [v.index for v in graph.vs if v["name"] in drug_ids]
    related_nodes = set(target_indices)

    # Include neighbors of target nodes
    for idx in target_indices:
        related_nodes.update(
            graph.neighbors(idx, mode="all")
        )  #"out" or "in" can be used here 

    subg = graph.induced_subgraph(list(related_nodes))
    return subg
