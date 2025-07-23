# Longevity hackathon
This is a project to showcase results obtained for the [Longevity hackathon](https://forimmortality.ai/ru/)

# Drug Research Platform

A Streamlit-based web application for biomedical drug research and discovery, integrating multiple pharmaceutical and biomedical databases for comprehensive drug analysis and exploration.

## 🚀 Features

- **Multi-Database Integration**: Combines data from DrKG, DrugBank, MeSH, SIDER, DOID, and HGNC
- **Interactive Web Interface**: Built with Streamlit for intuitive data exploration
- **Containerized Deployment**: Docker-based setup for consistent environments
- **Knowledge Graph Analysis**: Leverages drug repurposing knowledge graphs
- **Disease Ontology Integration**: Incorporates structured disease classifications

## 📋 Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)
- Minimum 4GB RAM recommended
- At least 2GB free disk space for data and containers

## 🗂️ Data Structure

The application integrates the following biomedical databases:

```
data/
├── doid/                    # Disease Ontology
│   └── doid.obo            # Disease classifications and relationships
├── drkg/                    # Drug Repurposing Knowledge Graph
│   ├── drkg.tsv            # Main knowledge graph data
│   ├── graph.gml           # Graph structure file
│   ├── relation_glossary.tsv # Relationship definitions
│   └── relation_glossary.xlsx
├── drugbank/                # DrugBank Database
│   └── drugbank_vocabulary.csv # Drug nomenclature and metadata
├── hgnc/                    # Human Gene Nomenclature Committee
│   └── HGNC_complete_set.tsv # Official gene symbols and names
├── mesh/                    # Medical Subject Headings
│   └── desc2025.xml        # Medical terminology hierarchy
├── sider/                   # Side Effect Resource
│   └── meddra_all_indications.tsv # Drug side effects and indications
├── drugbank_vocabulary.csv  # Additional drug vocabulary
└── entity_name_mapping.json # Entity name mappings across databases
```

### Database Sources

- **DOID**: [Disease Ontology](https://disease-ontology.org/) - Standardized disease classifications
- **DrKG**: [Drug Repurposing Knowledge Graph](https://github.com/gnn4dr/DRKG) - Comprehensive biomedical knowledge graph
- **DrugBank**: [DrugBank Database](https://go.drugbank.com/) - Pharmaceutical knowledge base
- **HGNC**: [HUGO Gene Nomenclature Committee](https://www.genenames.org/) - Official gene symbols
- **MeSH**: [Medical Subject Headings](https://www.nlm.nih.gov/mesh/) - NLM's controlled vocabulary
- **SIDER**: [Side Effect Resource](http://sideeffects.embl.de/) - Drug side effects database


### Google Drive Access files

Place the following files in the `access/` directory to enable Google Drive access:
`access/service_account.json`.

## 🛠️ Installation & Setup

### Option 1: Using Make (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd <project-directory>

# Build and start all services
make
```

### Option 2: Using Docker Compose Directly

```bash
# Set environment variables
export UID=$(id -u)
export GID=$(id -g)

# Build and start
docker compose build
docker compose up -d
```

## 🚀 Usage

### Accessing the Application

Once the containers are running, access the Streamlit application at:
```
http://localhost:8501
```

### Available Make Commands

```bash
make help     # Show all available commands
make build    # Build all containers
make up       # Start containers in detached mode
make down     # Stop all containers
make logs     # View container logs
make ps       # Show container status
make restart  # Restart services
make clean    # Clean volumes (⚠️ removes data)
```

### Development Commands

```bash
# Access container shell
make shell SERVICE=streamlit_app

# View logs in real-time
make logs

# Restart specific service
make restart SERVICE=streamlit_app
```

## 🔧 Configuration



### Port Configuration

- **Streamlit App**: Port 8501 (configurable in docker-compose.yml)

### Volume Mounts

- `./streamlit_app` → `/app/streamlit_app` (Application code)
- `./data` → `/app/data` (Database files)
- `./access` → `/app/access` (Access control files)

## 📁 Project Structure

```
.
├── docker-compose.yml      # Docker services configuration
├── Dockerfile             # Container build instructions
├── Makefile               # Development convenience commands
├── requirements.txt       # Python dependencies
├── project_config.py      # Project configuration
├── streamlit_app/         # Streamlit application code
│   └── root_page.py       # Main application entry point
├── app/                   # Core application modules
├── research_scripts/      # Research and analysis scripts
├── data/                  # Database files (see structure above)
└── access/                # Access control and authentication
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test with: `make build && make up`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📧 Contact

**Maintainers**: mikhail.solovyanov@gmail.com
