# Wrapper by miksolo for Vladislav scoring system
import pandas as pd
import numpy as np

from project_config import DRUG_PIVOT_PATH

from loguru import logger
from itertools import combinations



def normalize_cell(cell):
    """
    Ensure each cell is either:
     - an empty list (if it was NaN)
     - a plain Python list (if it was list-like)
     - unchanged otherwise (e.g. a scalar)
    """

    if isinstance(cell, list):
        return set(cell)

    if isinstance(cell, np.ndarray):
        return set(cell.tolist())

    if isinstance(cell, (tuple, set)):
        return cell
        
    if pd.isna(cell):
        return set()

    return cell


drug_pivot = pd.read_json(DRUG_PIVOT_PATH, orient="table").set_index("compound")
# apply to every cell
drug_pivot = drug_pivot.map(normalize_cell)


def gene_score(ref_row: pd.Series,
               cmp_row: pd.Series,
               gene_column: str = 'drug_gene') -> int:
    '''
    Compare gene_plus and gene_minus intaractions between two compound. 
    Return score for genes
    '''
    s = 0
    
    # logger.debug(f"Comparing genes for {ref_row.name} vs {cmp_row.name}")
    
    rp = set(ref_row[f'{gene_column}_plus'])
    rm = set(ref_row[f'{gene_column}_minus'])
    pp = set(cmp_row[f'{gene_column}_plus'])
    pm = set(cmp_row[f'{gene_column}_minus'])

    s += 2 * len(rp & pp)      # plus‑plus
    s += 2 * len(rm & pm)      # minus‑minus
    s -= 2 * len(rp & pm)      # plus‑minus conflict
    s -= 2 * len(rm & pp)      # minus‑plus conflict
    return s

def pathway_mf_score(ref_row: pd.Series,
                     cmp_row: pd.Series,
                     columns_for_score: list = ['gene_pathway', 'gene_function']) -> int:
    '''
    Compare pathways and molecular functions intaractions between two compound.
    Each interactions considered as half of common genes
    Return score for them
    '''
    s = 0
    
    for col in columns_for_score:
        rp = set(ref_row[f'{col}_plus'])
        rm = set(ref_row[f'{col}_minus'])
        pp = set(cmp_row[f'{col}_plus'])
        pm = set(cmp_row[f'{col}_minus'])
    
        s += len(rp & pp)      # plus‑plus
        s += len(rm & pm)      # minus‑minus
        s -= len(rp & pm)      # plus‑minus conflict
        s -= len(rm & pp)      # minus‑plus conflict
    return s

def disease_score(ref_row: pd.Series,
                  cmp_row: pd.Series,
                  disease_column: str = 'drug_disease') -> int:
    '''
    Compare common disease for two compounds. Compound may be associated with a disease or cure a disease.
    Minus score for every associated disease
    Return score for disease
    '''
    s = 0
    
    rp = set(ref_row[f'{disease_column}_plus'])
    rm = set(ref_row[f'{disease_column}_minus'])
    pp = set(cmp_row[f'{disease_column}_plus'])
    pm = set(cmp_row[f'{disease_column}_minus'])

    s += 2 * len(rp & pp)     # plus‑plus
    s -= 2* len(rm & pm)      # minus‑minus
    s += len(rp & pm)         # plus‑minus conflict
    s += len(rm & pp)         # minus‑plus conflict
    
    s += len(rp)  # plus for every cured disease
    s += len(pp)
    s -= len(rm)  # minus for every associated disease
    s -= len(pm)
    return s

def side_effects_score(ref_row: pd.Series,
                       cmp_row: pd.Series,
                       side_effects_column: str = 'drug_side_effect_plus') -> int:
    '''
    Compare side effects for two compounds. We penalized score for each side effect and additionally for each common side effects
    Return score for side effects
    '''
    s = 0
    
    ref_se = set(ref_row[side_effects_column])
    cmp_se = set(cmp_row[side_effects_column])

    s -= len(ref_se)                  # Minus for each side effect
    s -= len(cmp_se)  
    s -= 2 * len(ref_se & cmp_se)     # Minus for shared side effects
    return s

    
def score_pair(ref_compound: str,
               compare_compound: str,
               df: pd.DataFrame = drug_pivot) -> int:
    '''
    ref_row - row for reference compound
    cmp_row - row for compare compound
    '''
    ref_row = df.loc[ref_compound]
    cmp_row = df.loc[compare_compound]

    s = 0
    s += gene_score(ref_row, cmp_row)
    s += pathway_mf_score(ref_row, cmp_row)
    s += disease_score(ref_row, cmp_row)
    s += side_effects_score(ref_row, cmp_row)

    # logger.debug(f"Pair score {ref_row.name} vs {cmp_row.name}: {s} "
    #               f"(shared_se={shared}, |ref_se|={len(ref_se)}, |cmp_se|={len(cmp_se)})")
    return s

def score_against_all(ref_compound: str,
                      df: pd.DataFrame = drug_pivot) -> pd.Series:
    """
    Compute a Series of scores for ref_compound vs every other compound in df.
    The score for ref_compound vs itself is set to -100.
    """
    # logger.info(f"Scoring {ref_compound} against {len(df)-1} other compounds")
    ref_row = df.loc[ref_compound]
    if ref_row.empty:
        raise ValueError(f"Compound '{ref_compound}' not found in the DataFrame.")
    else:
        logger.info(f"Scoring {ref_compound} against {len(df)-1} other compounds in the DataFrame")
    scores = {}
    for compare_compound in df.index:
        if compare_compound == ref_compound:
            scores[compare_compound] = -100
            continue
        scores[compare_compound] = score_pair(ref_compound, compare_compound, df=df)

    result = pd.Series(scores, name=ref_compound)
    # logger.info("Completed scoring all pairs")
    result = result.sort_values(ascending=False)
    
    return result


def get_sorted_list(scores: pd.Series) -> list:
    """
    Get a sorted list of tuples (substance, score) from a Series.
    Returns a list of tuples sorted by score in descending order.
    """
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def get_n_best(scores: pd.Series, n: int = 10) -> pd.Series:
    """
    Get the top n scores from a Series.
    Returns a DataFrame with the top n scores.
    """
    if n <= 0:
        raise ValueError("Parameter 'n' must be a positive integer.")
    
    if n > len(scores):
        n = len(scores)
        
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    top_n = sorted_scores[:n]
    top_n_series = pd.Series(dict(top_n), name=scores.name)
    top_n_series.index.name = "compound"
    
    return top_n_series




def find_best_pair(substances_local: list, 
                   name_to_id_func,
                   df: pd.DataFrame = drug_pivot,
                   top_n: int = 1) -> list:
    """
    Find the best pair(s) of substances based on scoring.
    
    Args:
        substances_local: List of substance names (real names)
        name_to_id_func: Function to convert name to ID for score_pair
        df: DataFrame to use for scoring
        top_n: Number of top pairs to return (default: 1 for best pair only)
    
    Returns:
        List of tuples: [(score, name1, name2, id1, id2), ...]
    """
    if len(substances_local) < 2:
        logger.warning("Need at least 2 substances to find pairs")
        return []
    
    logger.info(f"Finding best pair(s) among {len(substances_local)} substances")
    
    best_pairs = []
    total_pairs = len(list(combinations(substances_local, 2)))
    processed = 0
    
    # Try all possible pairs
    for name1, name2 in combinations(substances_local, 2):
        # try:
        # Convert names to IDs
        id1 = name_to_id_func(name1)
        id2 = name_to_id_func(name2)
        
        id1_returned = name_to_id_func(name1).split("::")[1]
        id2_returned = name_to_id_func(name2).split("::")[1]
        
        # Skip if conversion failed
        if id1 is None or id2 is None:
            logger.debug(f"Skipping pair {name1}-{name2}: ID conversion failed")
            continue
            
        # Calculate score
        score = score_pair(id1, id2, df=df)
        
        # Store the result
        best_pairs.append((score, name1, name2, id1_returned, id2_returned))
        
        processed += 1
        if processed % 100 == 0:  # Progress logging
            logger.debug(f"Processed {processed}/{total_pairs} pairs")
                
        # except Exception as e:
        #     logger.warning(f"Error processing pair {name1}-{name2}: {e}")
        #     continue
    
    if not best_pairs:
        logger.warning("No valid pairs found")
        return []
    
    # Sort by score (highest first) and return top_n
    best_pairs.sort(key=lambda x: x[0], reverse=True)
    result = best_pairs[:top_n]
    
    logger.info(f"Best pair found: {result[0][1]} & {result[0][2]} with score {result[0][0]}")
    return result