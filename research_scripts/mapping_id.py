import pandas as pd
import json
import project_config
import xml.etree.ElementTree as ET
import obonet


def create_entity_name_mapping():
    # compound
    df_compound = pd.read_csv(project_config.PATH_DRUGBANK_VOCABULARY)
    df_compound["DrugBank ID"] = "Compound::" + df_compound["DrugBank ID"]
    mapping_compound = df_compound.set_index("DrugBank ID")["Common name"].to_dict()

    # disease
    tree = ET.parse(project_config.PATH_MESH)
    root = tree.getroot()

    mapping_disease = {}

    for record in root.findall(".//DescriptorRecord"):
        mesh_ui = record.findtext("DescriptorUI")
        name = record.find("DescriptorName/String").text
        if mesh_ui and name:
            mapping_disease[f"Disease::MESH:{mesh_ui}"] = name

    # DOID
    doid = obonet.read_obo(project_config.PATH_DOID)
    doid_to_name = {
        f"Disease::{node_id}": data.get("name", "")
        for node_id, data in doid.nodes(data=True)
        if node_id.startswith("DOID:")
    }

    # gene
    df_gene = pd.read_csv(project_config.PATH_HGNC, sep="\t")
    df_gene["HGNC ID"] = "Gene::" + df_gene["HGNC ID"].str.split(":").str[1]
    mapping_gene = df_gene.set_index("HGNC ID")["Approved symbol"].to_dict()

    # Mapping Side Effect
    df_side_effect = pd.read_csv(project_config.PATH_SIDER, sep="\t", header=None)
    df_side_effect[1] = "Side Effect::" + df_side_effect[1]
    mapping_side_effect = df_side_effect.set_index(1)[3].to_dict()

    entity_name_mapping = (
        mapping_compound
        | mapping_disease
        | doid_to_name
        | mapping_gene
        | mapping_side_effect
    )

    with open(project_config.PATH_ENTITY_NAME_MAPPING, "w") as f:
        json.dump(entity_name_mapping, f)
