from igraph import plot
import project_config

def plot_subgraph(
    subg,
    output_path=project_config.PATH_SUBGRAPH_PNG,
    layout_type="fr",
    vertex_size=20,
    edge_arrow_size=0.5,
    bbox=(1000, 1000),
    margin=50,
    show_labels=True,
    show_edge_labels=False,
    edge_color="gray"
):
    
    layout = subg.layout(layout_type)

    visual_style = {
        "layout": layout,
        "bbox": bbox,
        "margin": margin,
        "vertex_size": vertex_size,
        "edge_arrow_size": edge_arrow_size,
        "edge_color": edge_color,
    }

    if show_labels:
        visual_style["vertex_label"] = subg.vs["name"]
    if "color" in subg.vs.attributes():
        visual_style["vertex_color"] = subg.vs["color"]
    if show_edge_labels and "relation" in subg.es.attributes():
        visual_style["edge_label"] = subg.es["relation"]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plot(subg, target=output_path, **visual_style)
