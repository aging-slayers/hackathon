import json
import csv
from loguru import logger
import time

import pandas as pd
import numpy as np
from functools import lru_cache


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
        # logger.debug(f"List/array mapped: {cell} -> {mapped}")
        return mapped

    # 2) handle missing scalars
    if cell is None or pd.isna(cell):
        # logger.debug("Missing value encountered, leaving unchanged")
        return cell

    # 3) scalar mapping
    new_val = mapper.get(cell, cell)
    if new_val != cell:
        # logger.debug(f"Scalar mapped: {cell} -> {new_val}")
        pass
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
    except:
        return {}


substances_file = "data/drugbank/drugbank_vocabulary.csv"


@lru_cache(maxsize=1)
def load_substances():
    substances = {}
    with open(substances_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            substances[row[2].lower()] = row[0]
            if len(row) > 4:
                for synonym in row[5].split("|"):
                    substances[synonym.strip().lower()] = row[0]
    logger.info(f"Loaded {len(substances)} substances")
    return substances




substances = load_substances()

substances_dict = {v: k for k, v in substances.items()}


def find_substances(query: str) -> list[str]:
    """Deprecated"""
    ret = []
    for substance in substances.keys():
        if substance in query.lower():
            ret.append(substances[substance])
    return ret


def return_substances_id_from_list(substances_list: list[str], lower: bool = False) -> list[str]:
    """
        Return the list of substances IDs from the list of substances names.
    """
    ret = []
    for substance in substances_list:
        if lower:
            substance = substance.lower().strip()
        if substance in substances:
            ret.append(substances[substance])
        else:
            logger.warning(f"Substance {substance} not found in the vocabulary.")
    return ret

"""{'common name': 'DrugBank ID',
 'synonyms': 'DrugBank ID',
 'lepirudin': 'DB00001',
 '[leu1, thr2]-63-desulfohirudin': 'DB00001',
 'desulfatohirudin': 'DB00001',
 'hirudin variant-1': 'DB00001',
 'lepirudin recombinant': 'DB00001',"""

def id_to_name(id:str) -> str:
    """
        Convert substance ID to its name.
    """
    if id in substances_dict:
        return substances_dict[id]
    else:
        logger.warning(f"Substance ID {id} not found in the vocabulary.")
        return id

def name_to_id(name: str) -> str:
    """
        Convert substance name to its ID. For Scoring purposes ONLY
    """
    if name.lower() in substances:
        return f"Compound::{substances[name.lower()]}"
    else:
        logger.warning(f"Substance name {name} not found in the vocabulary.")
        return name