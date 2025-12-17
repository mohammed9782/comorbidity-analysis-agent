# Mission 1: Data Ingestion & Graph Modeling

## 1. Objective
Write a robust Python script to ingest Austrian comorbidity data (Adjacency Matrices and Contingency Tables) into Neo4j Aura.

## 2. Inputs (Context)
- **Source Directory**: `./Data/`
  - `Adjacency Matrices/`: Contains CSVs where rows/cols are ICD-10 codes, values are Phi-correlations.
  - `Contingency Tables/`: Contains Risk Ratios.
  - `Prevalence/`: Contains general population stats.

## 3. The Graph Schema (Target State)
The Agent must implement this exact schema in Neo4j:

**Nodes:**
- `(:Disease {code: "E11", name: "Type 2 diabetes...", prevalence: 0.05})`
  - *ID Strategy*: Use ICD-10 code as the unique constraint/index.

**Relationships:**
- `(:Disease)-[:CO_OCCURS_WITH {weight: 0.8, risk_ratio: 2.5}]-(:Disease)`
  - *Note*: Relationships are undirected (symmetrical).

## 4. Implementation Tasks
- [ ] **Database Connection**: Create `src/utils/db.py` using the official `neo4j` Python driver. Read credentials from env vars.
- [ ] **Parser**: Create `src/ingestion/parser.py` using Pandas to read the Adjacency Matrix CSV.
- [ ] **Loader**: Create `src/ingestion/loader.py`.
    - Use `UNWIND` logic (Cypher batching) to insert nodes/edges efficiently (do not insert 1 by 1).
    - Handle missing keys or NaNs gracefully.
- [ ] **Verification**: Create a script `src/ingestion/verify.py` that asserts:
    - Total Node count > 0.
    - Total Relationship count > 0.
    - Returns a sample path between two diseases.

## 5. Definition of Done
- Script `python src/ingestion/loader.py` runs without errors.
- A Cypher query `MATCH (n:Disease) RETURN count(n)` returns the expected number of ICD codes (~1,080).