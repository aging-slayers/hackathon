import pandas as pd
import project_config
import json
import time

from research_scripts.find_id_compound import find_id_compound
from research_scripts.get_actual_relations import get_actual_relations
from research_scripts.loading_graph import build_igraph_from_triplets
from research_scripts.filtering_graph import filter_graph
from research_scripts.mapping_id import create_entity_name_mapping

from loguru import logger

start = time.time()
triplets = pd.read_csv(project_config.PATH_DRKG, sep='\t', header=None).values.tolist()
# graph = ig.read(project_config.PATH_GRAPH, format="gml")
logger.info(f"Loaded graph in {time.time() - start}s...")
  

def get_id_to_name_mapping():
    """Load the entity name mapping from a JSON file."""
    if not project_config.PATH_ENTITY_NAME_MAPPING.exists():
        create_entity_name_mapping()
        logger.debug("Entity name mapping created.")
    
    with open(project_config.PATH_ENTITY_NAME_MAPPING, "r") as f:
        entity_name_mapping = json.load(f)
    
    return entity_name_mapping

def run_subgraph_builder(drugs, map_readable_names=True):
    global triplets
    drug_ids = find_id_compound(drugs)
    
    logger.debug(f"Creating graph for the drugs: {', '.join(drugs)} with IDs: {', '.join(drug_ids)}")
    actual_relations = get_actual_relations(drug_ids)
    actual_triplets = [triplet for triplet in triplets if triplet[1] in actual_relations]
    
    graph = build_igraph_from_triplets(actual_triplets)
    filt_graph = filter_graph(graph, drug_ids)

    if map_readable_names:
        filt_graph.vs['name'] = [get_id_to_name_mapping().get(name, name) for name in filt_graph.vs['name']]
    
    return filt_graph, list(drug_ids)
