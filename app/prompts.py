
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

TASKS = {
    "compare": "Compare two or more substances in the query. Describe combination of substances mentioned in the query with respect to their effects on anti-aging",
    "combinations": "Find suitable combinations of the substances mentioned in the query. Concentrate around the effects of the combination of the substances rather than effects of the individual substance",
    "single": "Find a single substance that is mentioned in the query with respect to their effects on anti-aging",
    "tested": "Was the substance mentioned in the query tested on a specific species",
    # "effects": "Describe the effects of the substance mentioned in the query",
    "suggest": "Suggest the drugs and active substances that are suitable for the request in the area of longevity and anti-aging",
    "help": "User asks to explain what the system can do and how to use it. Explain following the tasks below:",
}

GRAPH_NEEDED = [
    "compare",
    "combinations",
    "single"
]

SCORING_NEEDED = [
    "compare",
    "combinations",
]

DETERMINE_TASK_PROMPT = "Check if the query provided belongs to one of the following task, or return WRONGTASK if the query belongs to none of them. Return only the label of the task."

GENERAL_PROMPT = "Here is the task and the query with respect to the task of longevity. Respond to the task as precise as possible. Return the response in a few sentences."
DENY_PROMPT = "Return a polite denial to perform the task requested because the system is designed to help primarily with longevity research tasks"

FIND_SUBSTANCES_PROMPT = """Find any substances in the query below.
Return a list of original words from text separated by ',' without spaces after ','. Do not separate one substance with ',' if it takes more than one word."""

GRAPH_PROMPT = "Additional information below includes a subgraph displaying relations between those substances in JSON format. Use it to form the response as a ground truth. Do not mention the work JSON in the output"
