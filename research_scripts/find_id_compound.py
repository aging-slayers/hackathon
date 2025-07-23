import pandas as pd
import project_config


def match_exact(val, drugs):
    return any(drug.lower() == val.strip().lower() for drug in drugs)


def find_id_compound(drugs):
    """
    Find DrugBank IDs for compounds based on exact matches in the DrugBank vocabulary.
    Args:
        drugs (list): List of drug names to match against the DrugBank vocabulary.
    Returns:
        list: List of DrugBank IDs for compounds that match the provided drug names.
        Compound::<id> format.
    """
    drugbank = pd.read_csv(project_config.PATH_DRUGBANK)

    mask_exact = drugbank[["Common name", "Synonyms"]].apply(
        lambda col: col.map(lambda val: match_exact(str(val), drugs))
    )
    filt_drugbank = drugbank[mask_exact.any(axis=1)]
    drugs_id = [f"Compound::{id}" for id in filt_drugbank["DrugBank ID"].unique()]

    return drugs_id
