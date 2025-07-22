#!/usr/bin/env python3

from typing import List, Optional
from clients import query_llama
from prompts import *

# initialize with cached lists of tokens
substances = None
signal_paths = None

def process_pipeline(query: str, history: List[str]=[], graph: Optional[object]=None):
    """
        Handle next step of the dialogue
    """

    #== 1 substance found
    # Find combinations with rapamycin
    # Describe effects of rapamycin
    # Was rapamycin tested on ...

    #== 2+ substances
    # Find good combinations among the substances listed
    # Are those compatible for the purpose of aging?

    #== 0 substances
    # Find me combinations of medical substances that can contribute to longevity task
    # -> take random 10

    # Find substances that influence a specific signal pathway (protein/gene)

    # Find substances that were tested on mice/Labubus

    # Suggest me substances that make my life longer
    # -> take 10 top elements -> random

    #== Trash
    # Order me a pizza

def determine_task(query: str) -> str:
    # For production purposes, BERT should be fine-tuned here
    tasks = "\n".join([f"{k}:{v}" for k, v in TASKS.items()])
    prompt = f"{DETERMINE_TASK_PROMPT}\n\n{tasks}\nQuery:{query}"
    res = query_llama(prompt)
    return res

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