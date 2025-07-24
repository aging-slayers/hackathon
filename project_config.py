from pathlib import Path

# Корень проекта — папка, где находится config.py
BASE_DIR = Path(__file__).resolve().parent

# Построим абсолютные пути
SERVICE_ACCOUNT_FILE = BASE_DIR / "access/service_account.json"
PATH_DRKG = BASE_DIR / 'data/drkg/drkg.tsv'
PATH_GRAPH = BASE_DIR / 'data/drkg/graph.gml'
PATH_DRUGBANK = BASE_DIR / 'data/drugbank/drugbank_vocabulary.csv'
PATH_DRUGBANK_VOCABULARY = BASE_DIR / "data/drugbank/drugbank_vocabulary.csv"
PATH_MESH = BASE_DIR / "data/mesh/desc2025.xml"
PATH_DOID = BASE_DIR / "data/doid/doid.obo"
PATH_HGNC = BASE_DIR / "data/hgnc/HGNC_complete_set.tsv"
PATH_SIDER = BASE_DIR / "data/sider/meddra_all_indications.tsv"
PATH_ENTITY_NAME_MAPPING = BASE_DIR / "data/entity_name_mapping.json"
PATH_SUBGRAPH_PNG = BASE_DIR / "results/subgraph.png"
PATH_SUBGRAPH_JSON = BASE_DIR / "results/subgraph.json"
DRUG_PIVOT_FULL_PATH = BASE_DIR / "data/drug_pivot_full.json"
DRUG_PIVOT_PATH = BASE_DIR / "data/drug_pivot_with_id.json"