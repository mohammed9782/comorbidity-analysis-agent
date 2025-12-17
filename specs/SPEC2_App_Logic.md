# Mission 2: MCP Logic & LangGraph Orchestration

## 1. Objective
Build the application core that processes user queries, fetches graph data, verifies with PubMed, and synthesizes an answer using `fastmcp` and `langgraph`.

## 2. Architecture
**Frameworks**: `fastmcp` (Server), `langgraph` (Flow), `langchain_openai` (LLM).

## 3. The Agent Workflow (LangGraph)
Implement a state graph with the following nodes:

1.  **Node: `extract_entities`**
    - Input: User natural language (e.g., "risks for diabetes").
    - Logic: LLM extraction to find valid ICD-10 codes.
    - Output: List of codes `['E11']`.
2.  **Node: `query_knowledge_graph`**
    - Input: ICD codes.
    - Logic: Execute Cypher query to find neighbors with `weight > threshold`.
    - Output: JSON of related diseases and risk ratios.
3.  **Node: `verify_pubmed`**
    - Input: Top 3 related diseases.
    - Logic: Query PubMed API (using `Bio.Entrez` or simple HTTP) for abstracts containing both disease terms.
    - Output: Summarized snippets of medical evidence.
4.  **Node: `synthesize_answer`**
    - Input: Graph Data + PubMed Evidence.
    - Logic: Generate final user-facing advice.

## 4. Implementation Tasks
- [ ] **Neo4j Tool**: Wrap the DB connection from Mission 1 into a LangChain Tool.
- [ ] **PubMed Tool**: Implement a simple wrapper to search PubMed for "Disease A AND Disease B" and return the top abstract.
- [ ] **Graph Definition**: Define the `StateGraph` in `src/agent/graph.py`.
- [ ] **Server Entrypoint**: Create `src/server.py` using `FastMCP`. Expose the graph as a tool or resource.
- [ ] **Prompts**: Create `prompts/synthesis.md` and `prompts/extraction.md` to keep prompts out of Python code.

## 5. Definition of Done
- Running `mcp dev src/server.py` starts the server successfully.
- The Agent can handle the query: "I have hypertension (I10). What else am I at risk for?"
- The response includes **statistical data** (from Neo4j) AND **literature references** (from PubMed).