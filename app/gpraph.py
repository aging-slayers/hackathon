import igraph as ig
import project_config
import json

from research_scripts.find_id_compound import find_id_compound
from research_scripts.get_actual_relations import get_actual_relations
from research_scripts.loading_graph import loading_graph
from research_scripts.filtering_graph import filter_graph
from research_scripts.mapping_id import create_entity_name_mapping
from research_scripts.visualisation import plot_subgraph
from research_scripts.save_graph import save_igraph_as_json
from research_scripts.coloring_edges import coloring_edges


from loguru import logger



def get_id_to_name_mapping():
    """Load the entity name mapping from a JSON file."""
    if not project_config.PATH_ENTITY_NAME_MAPPING.exists():
        create_entity_name_mapping()
        logger.debug("Entity name mapping created.")
    
    with open(project_config.PATH_ENTITY_NAME_MAPPING, "r") as f:
        entity_name_mapping = json.load(f)
    
    return entity_name_mapping

def run_subgraph_builder(drugs):
    if not project_config.PATH_GRAPH.exists():
        logger.debug("Loading graph from DRKG dataset...")
        loading_graph(project_config.PATH_GRAPH)
        logger.debug("Graph loaded from DRKG dataset.")
    graph = ig.read(project_config.PATH_GRAPH, format="gml")
    
    drug_ids = find_id_compound(drugs)
    
    logger.debug(f"Creating graph for the drugs: {', '.join(drugs)} with IDs: {', '.join(drug_ids)}")
    
    actual_relations = get_actual_relations(drug_ids)
    
    filt_graph = filter_graph(graph, drug_ids, actual_relations)

    entity_name_mapping = get_id_to_name_mapping()
    
    filt_graph.vs['name'] = [entity_name_mapping.get(name, name) for name in filt_graph.vs['name']]
    
    return filt_graph