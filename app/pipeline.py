#!/usr/bin/env python3

from loguru import logger
from typing import List, Optional
import pandas as pd

from app.clients import query_llama
from app.prompts import DETERMINE_TASK_PROMPT, GENERAL_PROMPT, \
        DENY_PROMPT, TASKS, GRAPH_NEEDED, FIND_SUBSTANCES_PROMPT, GRAPH_PROMPT, SCORING_NEEDED
from app.gpraph import run_subgraph_builder
from app.substance_mapper import create_json_for_llm, load_substances, substances, substances_dict, id_to_name, name_to_id, find_substances
from app.scoring import score_against_all, score_pair, get_n_best, find_best_pair

entities_file = "data/entity_name_mapping.json"
substances_file = "data/drugbank/drugbank_vocabulary.csv"

# Parameters for short queries with higher expected determination
llama_params_det = {
        "max_tokens": 80,
        "temperature": 0.45
    }


def check_substance_in_vocabulary(substance: str) -> bool:
    """
        Check if the substance is in the local vocabulary.
        Returns True if substance is found, False otherwise.
    """
    return substance.lower() in substances.keys() or substance in substances.values()

def find_substances_llm(query: str) -> List[str]:
    """
        Use LLM to find substances in the query.
        This is a fallback method if the substances are not found in the local vocabulary.
    """
    response = query_llama(f"{FIND_SUBSTANCES_PROMPT}\nQuery: {query}", params=llama_params_det)
    ret_substances = list()
    substances_found = response.split(",")
    
    for substance in substances_found:
        ret_substances.append(substance.lower().strip())
    return ret_substances if response else []

def determine_task(query: str) -> str:
    # For production purposes, BERT should be fine-tuned here
    tasks = "\n".join([f"{k}:{v}" for k, v in TASKS.items()])
    prompt = f"{DETERMINE_TASK_PROMPT}\n\n{tasks}\nQuery:{query}"
    res = query_llama(prompt, params=llama_params_det)
    return res


def process_pipeline(query: str, history: List[str]=[], graph: Optional[object]=None) -> dict:
    """
        Handle next step of the dialogue
    """
    
    response = {'text': '', 'graph': graph, 'history': history, 'substances': [], "scoring_info": None}
    logger.debug(f"Query received: {query}")
    discovered_class = determine_task(query)
    logger.info(f"Query: {query} -> {discovered_class}")
    prompt = f"{DENY_PROMPT}\n\nTask: {query}"
    if discovered_class in TASKS.keys():
        
        if discovered_class == "help":
            prompt = f"{GENERAL_PROMPT}\n\n{TASKS[discovered_class]}\nTasks which you can do:{TASKS}\nQuery: {query}"
            
        elif discovered_class in GRAPH_NEEDED:
            prompt = f"{GENERAL_PROMPT}\n\n{TASKS[discovered_class]}\nTask: {query}"
            # Prepare the graph if needed
            substances_local = find_substances_llm(query)
            logger.info(f"Found substances in query: {substances_local}")
            for substance in substances_local:
                if not check_substance_in_vocabulary(substance):
                    logger.warning(f"Substance {substance} not found in the vocabulary. Trying to find it with LLM...")
                    substances_local.remove(substance)
            

            
            
            if len(substances_local) == 0:
                prompt = f"Please ask user to provide a query that contains at least one substance from the DrugBank vocabulary."
            else:
                # Normal case graph is needed and substances are found
                
                if discovered_class in SCORING_NEEDED:
                    # Calculate scoring
                    if discovered_class == "combinations":
                        # Find the best combinations of substances and append the best pair to substance for graph
                        
                        substance_id = name_to_id(substances_local[0])  # Take the first substance for scoring
                        logger.info(f"Scoring substance {substances_local[0]}: {substance_id} against all other substances")
                        
                        scores = score_against_all(substance_id)
                        top: pd.Series = get_n_best(scores, n=5)
                        top_id = top.index[0].split("::")[1]
                        top_subst = id_to_name(top_id)
                        substances_comp = [substances_local[0], top_subst]
                        logger.info(f"Best scoring substance for {substances_local[0]} is {top_subst} with score {top.iloc[0]}")
                        
                        response['scoring_info'] = "Scoring information:\n" + \
                            f"Substance {substances_local[0]} scored against all other substances:\n{top.to_string()}\n" +\
                            f"Best scoring substance is {top_subst} with score {top.iloc[0]}.\n" + \
                            f"Substances for final graph: {substances_comp}"
                        
                    elif discovered_class == "compare":
                        if len(substances_local) > 2:
                            # Now we need to find best scoring for compare.
                            # Find best pair of substances
                            logger.info(f"Finding best pair of substances from {substances_local}")
                            best_score, name1, name2, id1, id2 = find_best_pair(
                                substances_local,
                                name_to_id_func=name_to_id,
                                top_n=1
                            )
                            substances_comp = [name1, name2]
                        
                            response['scoring_info'] = f"Best pair found: {name1} ({id1}) and {name2} ({id2}) with score {best_score}"
                        if len(substances_comp) == 2:
                            logger.info(f"COMPARE==2: Substances for graph: {substances_comp}")
                            substances_local = substances_comp
                    else:
                        substances_comp = substances_local[:2]
                llama_params_ans = {
                    "max_tokens": 3000,
                    "temperature": 0.5
                }

                response['substances'] = substances_comp
                logger.info(f"Found substances by LLM: {substances_local}. Try to find in the DrugBank vocabulary and bulding a graph for {substances_comp}")
                response['graph'], substance_ids = run_subgraph_builder(substances)
                logger.info(f"Subgraph built with {len(response['graph'].vs)} vertices and {len(response['graph'].es)} edges.")
                supplemental_json = create_json_for_llm(substance_ids)
                # logger.debug(json.dumps(supplemental_json, indent=4))
                if supplemental_json and len(supplemental_json) > 2:
                    prompt = f"{GENERAL_PROMPT}\n\n{TASKS[discovered_class]}\n{GRAPH_PROMPT}\n{supplemental_json}\nTask: {query}"

                if response['scoring_info'] is not None:
                    prompt += f"\nScoring info:\n{response['scoring_info']}"

        else:
            prompt = f"{GENERAL_PROMPT}\n\n{TASKS[discovered_class]}\nQuery: {query}"

    # logger.debug(response['graph'])
    response['text'] = query_llama(prompt, params=llama_params_ans)
    logger.debug(f"Query to LLM: {prompt}")
    logger.debug(f"LLM response: {response['text']}")
    logger.info(f"Sending response: {response['text'][:120]}...")
    return response


if __name__ == "__main__":
    tasks = [
        "Find combinations with rapamycin",
        "Are rapamycin and betaine compatible",
        "Find me combinations of medical substances that can contribute to longevity task",
        "Find substances that were tested on mice",
        "Find substances that were tested on Labubus",
        "Suggest me substances that make my life longer",
        "Order me a pizza"
    ]
    for task in tasks:
        discovered_class = "" #determine_task(task)
        print(f"Task: {task} -> {discovered_class}")

    res = find_substances(tasks[1])
    print(f"Sent: {tasks[1]} -> {res} ({[substances_dict[r] for r in res]})")

    res = find_substances("Hello")
    print(f"Sent: Hello -> {res} ({[substances_dict[r] for r in res]})")
