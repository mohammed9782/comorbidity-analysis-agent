import os
import json
from typing import TypedDict, List, Any, Dict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.agent.tools import query_neo4j, search_pubmed

# Define State
class AgentState(TypedDict):
    messages: List[Any]
    user_query: str
    entities: List[str]
    graph_data: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    exploration_mode: bool

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Nodes ---

def extract_entities(state: AgentState):
    """Extracts ICD codes from user query."""
    query = state["user_query"]
    
    with open("prompts/extraction.md", "r") as f:
        prompt_template = f.read()
        
    prompt = prompt_template.format(user_query=query)
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        # Clean markdown code blocks if present
        content = response.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        codes = data.get("codes", [])
    except:
        codes = []
        
    return {"entities": codes}

def query_knowledge_graph(state: AgentState):
    """Queries Neo4j for each extracted entity."""
    entities = state["entities"]
    all_results = []
    
    for code in entities:
        results = query_neo4j(code)
        for r in results:
            r["source_code"] = code # Track source
            all_results.append(r)
            
    # Deduplicate based on target code
    seen = set()
    unique_results = []
    for r in all_results:
        if r["code"] not in seen:
            unique_results.append(r)
            seen.add(r["code"])
            
    # Check if we need exploration mode
    exploration_mode = len(unique_results) == 0
    
    return {"graph_data": unique_results, "exploration_mode": exploration_mode}

async def verify_pubmed(state: AgentState):
    """Verifies relationships using PubMed."""
    graph_data = state["graph_data"]
    exploration_mode = state["exploration_mode"]
    entities = state["entities"]
    evidence = []
    
    if not exploration_mode:
        # Verify top 3 graph findings
        top_results = sorted(graph_data, key=lambda x: x["weight"], reverse=True)[:3]
        for item in top_results:
            source = item["source_code"]
            target = item["name"]
            query = f"{source} AND {target} AND (comorbidity OR risk)"
            articles = await search_pubmed(query)
            for art in articles:
                art["context"] = f"Link between {source} and {target}"
                evidence.append(art)
    else:
        # Exploration mode: Search for general risks for the source entities
        for code in entities:
            query = f"{code} AND (comorbidity OR risk factors OR complications)"
            articles = await search_pubmed(query)
            for art in articles:
                art["context"] = f"General risks for {code}"
                evidence.append(art)
                
    return {"evidence": evidence}

def synthesize_answer(state: AgentState):
    """Generates the final response."""
    with open("prompts/synthesis.md", "r") as f:
        prompt_template = f.read()
        
    prompt = prompt_template.format(
        user_query=state["user_query"],
        entities=state["entities"],
        graph_data=json.dumps(state["graph_data"], indent=2),
        evidence=json.dumps(state["evidence"], indent=2)
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"messages": [response]}

# --- Graph Definition ---

workflow = StateGraph(AgentState)

workflow.add_node("extract_entities", extract_entities)
workflow.add_node("query_knowledge_graph", query_knowledge_graph)
workflow.add_node("verify_pubmed", verify_pubmed)
workflow.add_node("synthesize_answer", synthesize_answer)

workflow.set_entry_point("extract_entities")

workflow.add_edge("extract_entities", "query_knowledge_graph")
workflow.add_edge("query_knowledge_graph", "verify_pubmed")
workflow.add_edge("verify_pubmed", "synthesize_answer")
workflow.add_edge("synthesize_answer", END)

app = workflow.compile()
