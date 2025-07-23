import sys

sys.path.append("./")
from research_scripts.sheet_access import read_sheet

def get_actual_relations(drug_ids, url=None):
    if url is None:
        url = "https://docs.google.com/spreadsheets/d/1K8hHouDr78dD9PByzvtDdIXxFaqrjUXFFw_CNfJGdaE/edit?pli=1&gid=1987581174#gid=1987581174"

    if len(drug_ids) == 1:
        worksheet_name = "relation_glossary_1_drugs"

    elif len(drug_ids) == 2:
        worksheet_name = "relation_glossary_2_drugs"
    else:
        print("More than two drugs are provided. Please provide only one or two drugs.")
        sys.exit(1)

    relation_glossary = read_sheet(
        url=url,
        worksheet_name=worksheet_name,
    )
    actual_relations = relation_glossary[
        relation_glossary["Take_to_analysis"] == "yes"
    ]["Relation-name"].to_list()

    return actual_relations