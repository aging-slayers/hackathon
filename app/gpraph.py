import igraph as ig
import project_config

from research_scripts.find_id_compound import find_id_compound
from research_scripts.get_actual_relations import get_actual_relations
from research_scripts.loading_graph import loading_graph
from research_scripts.filtering_graph import filter_graph
from research_scripts.mapping_id import create_entity_name_mapping
from research_scripts.visualisation import plot_subgraph
from research_scripts.save_graph import save_igraph_as_json
from research_scripts.coloring_edges import coloring_edges


from loguru import logger

def run_subgraph_builder(drugs):
    if not project_config.PATH_GRAPH.exists():
        logger.debug("Loading graph from DRKG dataset...")
        loading_graph(project_config.PATH_GRAPH)
        logger.debug("Graph loaded from DRKG dataset.")
    graph = ig.read(project_config.PATH_GRAPH, format="gml")
    
    drug_ids = find_id_compound(drugs)
    
    actual_relations = get_actual_relations(drug_ids)
    
    filt_graph = filter_graph(graph, drug_ids, actual_relations)
        
    return filt_graph