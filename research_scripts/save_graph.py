import project_config
import json


def save_igraph_as_json(graph, filepath=project_config.PATH_SUBGRAPH_JSON):
    edge_attrs = graph.es.attributes()
    node_attrs = graph.vs.attributes()

    data = {
        "nodes": [
            {
                "id": v.index,
                "name": v["name"],
                "type": v["type"] if "type" in node_attrs else None,
            }
            for v in graph.vs
        ],
        "edges": [
            {
                "source": e.source,
                "target": e.target,
                "relation": e["relation"] if "relation" in edge_attrs else None,
            }
            for e in graph.es
        ],
    }

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
