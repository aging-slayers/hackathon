import pandas as pd
import re
import project_config
import difflib


def find_closest_name(drug, df):
    all_names = df["Common name"].dropna().unique().tolist()
    all_synonyms = df["Synonyms"].dropna().unique().tolist()
    candidates = all_names + all_synonyms
    match = difflib.get_close_matches(drug, candidates, n=1, cutoff=0.4)
    return match[0] if match else None


def match_exact(val, drug):
    return drug.lower() == val.strip().lower()

def match_partial(val, drug):
    return re.search(rf'\b{re.escape(drug.lower())}\b', str(val).lower()) is not None


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
    drugbank["Synonym_List"] = drugbank["Synonyms"].fillna("").apply(lambda x: [s.strip() for s in x.split("|")])



    drug_ids = []

    for drug in drugs:
        # точное совпадение с Common name
        mask_common = drugbank["Common name"].fillna("").apply(lambda val: match_exact(val, drug))

        # точное совпадение с любым из синонимов
        mask_synonym = drugbank["Synonym_List"].apply(lambda syns: any(match_exact(s, drug) for s in syns))

        filt_drugbank = drugbank[mask_common | mask_synonym]

        # если ничего не найдено — ищем наиболее похожее
        if filt_drugbank.empty:
            # объединяем список всех имён и синонимов
            all_names = drugbank["Common name"].dropna().tolist()
            all_synonyms = [s for sublist in drugbank["Synonym_List"] for s in sublist]
            candidates = all_names + all_synonyms

            match = difflib.get_close_matches(drug, candidates, n=1, cutoff=0.8)
            if match:
                matched = match[0]
                filt_drugbank = drugbank[
                    (drugbank["Common name"] == matched) |
                    (drugbank["Synonym_List"].apply(lambda syns: matched in syns))
                ]
            else:
                print(f"⚠️ Drug not found: {drug}")
                continue

        best_row = filt_drugbank.iloc[0]
        drug_id = best_row["DrugBank ID"]
        drug_ids.append(f"Compound::{drug_id}")
    return(drug_ids)