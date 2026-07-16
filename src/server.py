import asyncio
import logging
import sys
import json
from fastmcp import FastMCP, Context
from src.agent.graph import app
from src.utils.callbacks import MCPCallbackHandler
from dotenv import load_dotenv

# Configure logging to stderr (visible in Docker/Claude logs)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("medical-mcp")

load_dotenv()

# Initialize FastMCP Server
logger.info("Initializing FastMCP Server...")
mcp = FastMCP("GraphRAGgaeton")

@mcp.tool()
async def ask_doctor(query: str, ctx: Context = None) -> str:
    """
    Medical assistant focused on explainable risk analysis and discovery of potential comorbidities.
    Use this tool to answer user questions about health risks, comorbidities, and medical evidence.
    
    Args:
        query: The user's natural language query (e.g., "I have hypertension, what are the risks?").
        ctx: The MCP context for logging and progress updates.
    """
    logger.info(f"Received query: {query}")
    try:
        # Initial state
        initial_state = {
            "user_query": query,
            "messages": [],
            "entities": [],
            "graph_data": [],
            "evidence": [],
            "exploration_mode": False
        }
        
        # Setup callbacks
        callbacks = []
        if ctx:
            callbacks.append(MCPCallbackHandler(ctx))
        
        # Invoke LangGraph
        logger.info("Invoking LangGraph agent...")
        result = await app.ainvoke(initial_state, config={"callbacks": callbacks})
        
        # Extract final message
        final_message = result["messages"][-1]
        content = final_message.content
        
        # Append Sources & Methodology
        content += "\n\n---\n### Sources & Methodology\n"
        
        # 1. Graph Data
        graph_data = result.get("graph_data", [])
        if graph_data:
            content += "**Analyzed Comorbidities (Neo4j):**\n"
            # Deduplicate by code
            seen_codes = set()
            for item in graph_data:
                if item['code'] not in seen_codes:
                    content += f"- **{item['name']}** ({item['code']}): Risk Ratio {item.get('risk_ratio', 'N/A')}\n"
                    seen_codes.add(item['code'])
        else:
            content += "**Analyzed Comorbidities:** None found.\n"
            
        # 2. Evidence
        evidence = result.get("evidence", [])
        if evidence:
            content += "\n**Medical Evidence (PubMed):**\n"
            for item in evidence:
                content += f"- [{item.get('pmid', 'Link')}] {item.get('title', 'Untitled')} ({item.get('year', 'N/A')})\n"
        else:
            content += "\n**Medical Evidence:** No articles retrieved.\n"

        logger.info("Query processed successfully.")
        return content
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return f"Error processing query: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting MCP server via CLI...")
    mcp.run()

# Expose ASGI app for Uvicorn/Docker
# mcp.http_app() returns the Starlette/FastAPI app needed by Uvicorn
sse = mcp.http_app()
