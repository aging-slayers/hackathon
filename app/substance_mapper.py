import json
from loguru import logger
import time

import pandas as pd
import numpy as np


columns_pathway_function = [
    'gene_pathways_activated_by_drug',
    'gene_pathways_inhibited_by_drug',
    'molecular_function_activated_by_drug',
    'molecular_function_inhibited_by_drug'
]

def load_json_file(filepath):
    """
    Load JSON data from a file into a Python dict.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)  # parses file into dict/list
    return data

def process_mapping(ent_mapper):
    ent_mapper_new = {x:ent_mapper[x].split(':')[-1] for x in ent_mapper.keys()}
    ent_mapper_new['drug_disease_minus'] = 'disease_associated_with_drug'
    ent_mapper_new['drug_disease_plus'] = 'disease_cured_by_drug'
    ent_mapper_new['drug_gene_minus'] = 'genes_inhibited_or_suppressed_by_drug'
    ent_mapper_new['drug_gene_plus'] = 'genes_enhanced_or_activated_by_drug'
    ent_mapper_new['drug_side_effect_plus'] = 'side_effects_assosiated_with_drug'
    ent_mapper_new['gene_pathway_plus'] = 'gene_pathways_activated_by_drug'
    ent_mapper_new['gene_pathway_minus'] = 'gene_pathways_inhibited_by_drug'
    ent_mapper_new['gene_function_plus'] = 'molecular_function_activated_by_drug'
    ent_mapper_new['gene_function_minus'] = 'molecular_function_inhibited_by_drug'
    return ent_mapper_new

def map_cell(cell, mapper):
    """
    Map a cell value (which can be NaN, list, numpy array, or scalar) using mapper dict.
    - If list/array: map each element, keep original if not in mapper
    - If None/NaN: leave as is
    - Else (scalar): map if in mapper, else leave
    """
    # 1) handle lists and numpy arrays first
    if isinstance(cell, (list, np.ndarray)):
        mapped = [mapper.get(item, item) for item in cell]
        logger.trace(f"List/array mapped: {cell} -> {mapped}")
        return mapped

    # 2) handle missing scalars
    if cell is None or pd.isna(cell):
        logger.trace("Missing value encountered, leaving unchanged")
        return cell

    # 3) scalar mapping
    new_val = mapper.get(cell, cell)
    if new_val != cell:
        logger.debug(f"Scalar mapped: {cell} -> {new_val}")
    return new_val


def map_dataframe(df, entity_mapper):
    # 1) map all cells
    df_mapped = df.map(lambda x: map_cell(x, entity_mapper))
    logger.info("Finished mapping cell values")
    
    # 2) map row index
    logger.info("Mapping DataFrame index")
    new_index = [entity_mapper.get(idx, idx).lower() for idx in df_mapped.index]
    df_mapped.index = new_index

    logger.info("Mapping DataFrame columns")
    df_mapped.rename(columns=entity_mapper, inplace=True)
    return df_mapped

start = time.time()
drug_pivot = pd.read_json("data/drug_pivot_full.json", orient="table").set_index("compound")
ent_mapper_new = process_mapping(load_json_file('data/entity_name_mapping.json'))
drug_pivot_mapped = map_dataframe(drug_pivot, ent_mapper_new)
logger.info(f"Loaded substance mapping graph in {time.time() - start}s...")

def create_json_for_llm(compounds: list, drug_pivot=drug_pivot_mapped, mapper=ent_mapper_new) -> dict:
    try:
        drug_pivot_comp = drug_pivot.loc[compounds].dropna(axis=1, how='all').drop(columns=columns_pathway_function)
        return drug_pivot_comp.to_dict()
    except Exception as e:
        logger.error(e)
        return {}

