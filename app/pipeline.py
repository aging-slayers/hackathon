#!/usr/bin/env python3

from typing import List, Optional
from app.clients import query_llama
from app.prompts import *
from loguru import logger

# initialize with cached lists of tokens
substances = None
signal_paths = None

def find_substances(query: str) -> List[str]:
    
    return []

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
