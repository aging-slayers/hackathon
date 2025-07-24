#!/usr/bin/env python3

import csv
import json
from loguru import logger
from typing import List, Optional

from app.clients import query_llama
from app.prompts import DETERMINE_TASK_PROMPT, GENERAL_PROMPT, \
        DENY_PROMPT, TASKS, GRAPH_NEEDED, FIND_SUBSTANCES_PROMPT, GRAPH_PROMPT
from app.gpraph import run_subgraph_builder
from app.substance_mapper import create_json_for_llm

entities_file = "data/entity_name_mapping.json"
substances_file = "data/drugbank/drugbank_vocabulary.csv"

# Parameters for short queries with higher expected determination
llama_params_det = {
        "max_tokens": 80,
        "temperature": 0.45
    }


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
    


# initialize with cached lists of tokens
substances = load_substances()
substances_dict = {v: k for k, v in substances.items()}
signal_paths = None


def find_substances(query: str) -> List[str]:
    """Deprecated"""
    ret = []
    for substance in substances.keys():
        if substance in query.lower():
            ret.append(substances[substance])
    return ret

def return_substances_id_from_list(substances_list: List[str]) -> List[str]:
    """
        Return the list of substances IDs from the list of substances names.
    """
    ret = []
    for substance in substances_list:
        if substance in substances:
            ret.append(substances[substance])
        else:
            logger.warning(f"Substance {substance} not found in the vocabulary.")
    return ret


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
    
    response = {'text': '', 'graph': graph, 'history': history}
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
            substances = find_substances_llm(query)
            logger.info(f"Found substances in query: {substances}")
            for substance in substances:
                if not check_substance_in_vocabulary(substance):
                    logger.warning(f"Substance {substance} not found in the vocabulary. Trying to find it with LLM...")
                    substances.remove(substance)
            
            if len(substances) == 0:
                prompt = f"Please provide a query that contains at least one substance from the DrugBank vocabulary."
            else:
                logger.info(f"Found substances by LLM: {substances}. Try to find in the DrugBank vocabulary and bulding a graph")
                response['graph'] = run_subgraph_builder(substances)
                logger.info(f"Subgraph built with {len(response['graph'].vs)} vertices and {len(response['graph'].es)} edges.")
                supplemental_json = create_json_for_llm(substances)
                # logger.debug(json.dumps(supplemental_json, indent=4))
                if supplemental_json and len(supplemental_json) > 2:
                    prompt = f"{GENERAL_PROMPT}\n\n{TASKS[discovered_class]}\n{GRAPH_PROMPT}\n{supplemental_json}\nTask: {query}"

        else:
            prompt = f"{GENERAL_PROMPT}\n\n{TASKS[discovered_class]}\nQuery: {query}"

    # logger.debug(response['graph'])
    response['text'] = query_llama(prompt)
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
