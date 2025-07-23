#!/usr/bin/env python3

import csv
from typing import List, Optional
from loguru import logger

from app.clients import query_llama
from app.prompts import DETERMINE_TASK_PROMPT, GENERAL_PROMPT, DENY_PROMPT, TASKS

entities_file = "data/entity_name_mapping.json"
substances_file = "data/drugbank_vocabulary.csv"

def load_substances():
    substances = {}
    with open(substances_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            # DB00001,BTD00024 | BIOD00024,Lepirudin,138068-37-8,Y43GF64R34,"[Leu1, Thr2]-63-desulfohirudin | Desulfatohirudin | Hirudin variant-1 | Lepirudin | Lepirudin recombinant | R-hirudin",
            substances[row[2].lower()] = row[0]
            if len(row) > 4:
                for synonym in row[5].split("|"):
                    substances[synonym.strip().lower()] = row[0]
    logger.info(f"Loaded {len(substances)} substances")
    return substances
    


# initialize with cached lists of tokens
substances = load_substances()
signal_paths = None


def find_substances(query: str) -> List[str]:
    ret = []
    for substance in substances.keys():
        if substance in query.lower():
            ret.append(substances[substance])
    return ret

def determine_task(query: str) -> str:
    # For production purposes, BERT should be fine-tuned here
    tasks = "\n".join([f"{k}:{v}" for k, v in TASKS.items()])
    prompt = f"{DETERMINE_TASK_PROMPT}\n\n{tasks}\nQuery:{query}"
    res = query_llama(prompt)
    return res


def process_pipeline(query: str, history: List[str]=[], graph: Optional[object]=None):
    """
        Handle next step of the dialogue
    """
    discovered_class = determine_task(query)
    logger.info(f"Query: {query} -> {discovered_class}")
    prompt = f"{DENY_PROMPT}\n\nTask:{query}"
    if discovered_class in TASKS.keys():
        
        if discovered_class == "help":
            prompt = f"{GENERAL_PROMPT}\n\n{TASKS[discovered_class]}\nTasks which you can do:{TASKS}\nQuery:{query}"
        else:
            prompt = f"{GENERAL_PROMPT}\n\n{TASKS[discovered_class]}\nQuery:{query}"
    response = query_llama(prompt)
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
        discovered_class = determine_task(task)
        print(f"Task: {task} -> {discovered_class}")

    res = find_substances(tasks[1])
    print(f"Sent: {tasks[1]} -> {res} ({substances[res[0]]})")
