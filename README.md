# Comorbidity Analysis Agent

A machine learning pipeline for analyzing disease comorbidities using Neo4j and LLM-powered insights.

## 🎯 Project Overview

This project implements three missions:

1. **Mission 1: Data Ingestion** - Load Austrian comorbidity data into Neo4j
2. **Mission 2: MCP Agent Logic** - Build LLM-powered query agent with PubMed verification
3. **Mission 3: Cloud Deployment** - Deploy to Google Cloud Run

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Neo4j Aura instance
- OpenAI API key (for Mission 2+)
- Mamba or pip (we recommend Mamba)

### Setup with Mamba (Recommended)

```bash
# 1. Clone and navigate to project
cd ~/projects/hackathon\ paris\ 2025/comorbidity-analysis-agent

# 2. Create Mamba environment
mamba env create -f environment.yml
mamba activate comorbidity-agent

# 3. Configure credentials
cat > .env << 'EOF'
NEO4J_URI=bolt://your-neo4j-instance:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
OPENAI_API_KEY=your-openai-key  # For Mission 2+
EOF

# 4. Run data ingestion
python -m src.ingestion.loader_main

# 5. Verify loading
python -m src.ingestion.verify
```

### Setup with Pip

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Then follow steps 3-5 above
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **MAMBA_COMPLETE_SETUP.md** | Mamba vs Pip comparison and full setup guide |
| **MAMBA_SETUP.md** | Detailed Mamba installation and commands |
| **MISSION1_GUIDE.md** | Step-by-step Mission 1 implementation (7 phases) |
| **MISSION1_CHECKLIST.md** | Quick checklist for Mission 1 tasks |
| **specs/SPEC1_Data_Layer.md** | Technical specification for data layer |
| **specs/SPEC2_App_Logic.md** | Technical specification for agent logic |
| **specs/SPEC3_Infra.md** | Technical specification for deployment |

## 📂 Project Structure

```
comorbidity-analysis-agent/
├── Data/                           # Source data
│   ├── 1.Prevalence/              # Disease prevalence statistics
│   ├── 2.ContingencyTables/       # Risk ratio tables
│   └── 3.AdjacencyMatrices/       # Disease correlation matrices
├── src/                            # Python source code
│   ├── utils/
│   │   └── db.py                  # Neo4j connection management
│   ├── ingestion/
│   │   ├── parser.py              # CSV data parsing
│   │   ├── loader.py              # Neo4j data loading
│   │   ├── loader_main.py         # Main ingestion script
│   │   └── verify.py              # Data verification
│   └── agent/                      # (Mission 2+)
│       ├── graph.py               # LangGraph workflow
│       ├── tools/                 # Neo4j and PubMed tools
│       └── prompts/               # LLM prompts
├── specs/                          # Technical specifications
├── .env                            # Local credentials (not in git)
├── environment.yml                 # Mamba environment spec
├── requirements.txt                # Pip dependencies
└── README.md                       # This file
```

## 🔧 Commands Reference

### Mamba Commands

```bash
# Activate environment
mamba activate comorbidity-agent

# List installed packages
mamba list

# Install new package
mamba install -c conda-forge package-name

# Update environment
mamba env update -f environment.yml --prune

# Deactivate environment
mamba deactivate
```

### Project Commands

```bash
# Run data ingestion
python -m src.ingestion.loader_main

# Verify data was loaded
python -m src.ingestion.verify

# Test Neo4j connection
python -c "from src.utils.db import get_connection; get_connection().verify_connection()"
```

## 📋 Mission Status

- [x] **Mission 1: Data Ingestion** - Core modules implemented
  - [x] Database connection (`src/utils/db.py`)
  - [x] CSV parser (`src/ingestion/parser.py`)
  - [x] Data loader with UNWIND batching (`src/ingestion/loader.py`)
  - [x] Verification script (`src/ingestion/verify.py`)
  - [ ] Load all data files
  - [ ] Add prevalence data
  
- [ ] **Mission 2: MCP Agent Logic**
  - [ ] Neo4j query tool
  - [ ] PubMed search tool
  - [ ] LangGraph workflow
  - [ ] FastMCP server
  
- [ ] **Mission 3: Cloud Deployment**
  - [ ] Dockerfile
  - [ ] Cloud Build configuration
  - [ ] Cloud Run deployment

## 🗂️ Data Sources

### Adjacency Matrices
- Location: `Data/3.AdjacencyMatrices/`
- Format: CSV with disease codes as rows and columns
- Values: Phi-correlations between diseases
- Files by demographics: age groups (1-8) and years (2003-2014)
- Stratified by: Sex (Male/Female) and Disease Type (Blocks/Chronic/ICD)

### Contingency Tables
- Location: `Data/2.ContingencyTables/`
- Format: R dataframe (.rds files)
- Contains: Risk ratios for disease pairs

### Prevalence Data
- Location: `Data/1.Prevalence/`
- Format: CSV
- Contains: Population prevalence by disease, age, sex, year

## 🗄️ Neo4j Graph Schema

### Nodes
```cypher
(:Disease {code: "E11", name: "Type 2 diabetes", prevalence: 0.05})
```

### Relationships
```cypher
(:Disease)-[:CO_OCCURS_WITH {weight: 0.8, risk_ratio: 2.5}]-(:Disease)
```

## 🔐 Environment Variables

Create a `.env` file in the project root (never commit this):

```env
# Neo4j Configuration
NEO4J_URI=bolt://your-instance:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password

# OpenAI Configuration (Mission 2+)
OPENAI_API_KEY=sk-...

# PubMed Configuration (Mission 2+)
PUBMED_EMAIL=your-email@example.com
```

## 🧪 Testing

```bash
# Run verification script
python -m src.ingestion.verify

# Check Neo4j via Cypher (in Neo4j Browser)
MATCH (d:Disease) RETURN count(d)                    # Count nodes
MATCH ()-[r:CO_OCCURS_WITH]-() RETURN count(r)      # Count relationships
MATCH (a:Disease)-[r]-(b:Disease) RETURN a, r, b LIMIT 5  # Sample paths
```

## 📖 Implementation Guides

### Phase 1: Install and Configure
- Follow **MAMBA_COMPLETE_SETUP.md** for environment setup

### Phase 2: Implement Mission 1
- Use **MISSION1_GUIDE.md** for detailed step-by-step instructions
- Check off tasks in **MISSION1_CHECKLIST.md**
- Complete all 7 phases

### Phase 3: Implement Mission 2
- Follow **specs/SPEC2_App_Logic.md**
- Implement LangGraph workflow
- Build MCP server with FastMCP

### Phase 4: Deploy to Cloud
- Follow **specs/SPEC3_Infra.md**
- Create Docker image
- Configure Cloud Build
- Deploy to Cloud Run

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes and test thoroughly
3. Commit with clear messages: `git commit -m "feat: description"`
4. Push to remote: `git push origin feature/my-feature`
5. Create a Pull Request

## 📝 Git Workflow

```bash
# Check git status
git status

# Add files
git add src/ .gitignore environment.yml

# Commit
git commit -m "feat: implement mission 1 data ingestion"

# View history
git log --oneline

# Push to remote
git push origin neo4j-graph
```

## 🐛 Troubleshooting

### Environment Issues
See **MAMBA_SETUP.md** section "Troubleshooting"

### Neo4j Connection Issues
- Verify credentials in `.env`
- Check Neo4j instance is running
- Confirm URI format: `bolt://host:port`

### Import Errors
```bash
# Ensure environment is activated
mamba activate comorbidity-agent

# Verify imports work
python -c "import pandas, neo4j, dotenv; print('✓ OK')"
```

### Slow Loading
- Increase batch size in `src/ingestion/loader.py`
- Check Neo4j network connectivity
- Monitor Neo4j resource usage

## 📚 Resources

- [Neo4j Python Driver](https://neo4j.com/docs/api/python-driver/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/)
- [Mamba Documentation](https://mamba.readthedocs.io/)
- [LangGraph](https://python.langchain.com/docs/langgraph)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Google Cloud Run](https://cloud.google.com/run/docs)

## 📄 License

[Specify your license]

## 👥 Team

- **Project Lead**: Mohammed
- **Architecture**: Neo4j + LLM Agent
- **Deployment**: Google Cloud

## 📞 Support

For issues or questions:
1. Check **MISSION1_GUIDE.md** troubleshooting section
2. Review **specs/** for technical details
3. Check **MAMBA_SETUP.md** for environment issues

---

**Status**: Mission 1 implementation in progress  
**Last Updated**: December 17, 2025  
**Current Branch**: neo4j-graph
