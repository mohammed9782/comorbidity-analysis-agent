from typing import Any, Dict, List, Optional
from uuid import UUID
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from fastmcp import Context

class MCPCallbackHandler(BaseCallbackHandler):
    """
    Callback handler that logs LangChain events to the MCP Context.
    This allows the user to see real-time progress in the Claude Desktop client.
    """
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        # We can log high-level state changes here if needed
        pass

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        tool_name = serialized.get("name")
        if tool_name == "query_neo4j":
            self.ctx.info(f"🔍 Querying Knowledge Graph for: {input_str}")
        elif tool_name == "search_pubmed":
            self.ctx.info(f"📚 Searching PubMed for: {input_str}")

    def on_tool_end(self, output: Any, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        # The output is usually the return value of the tool function
        # We can inspect it to provide more detailed logs
        
        # We need to infer which tool just finished. 
        # LangChain's callback interface doesn't pass the tool name to on_tool_end directly 
        # in a convenient way without tracking state, but we can try to infer from the output structure.
        
        if isinstance(output, list):
            if not output:
                self.ctx.info("⚠️ No results found.")
                return

            first_item = output[0]
            
            # Check if it's Neo4j data (has 'risk_ratio', 'weight', 'code')
            if isinstance(first_item, dict) and "risk_ratio" in first_item:
                diseases = [item.get("name", "Unknown") for item in output[:5]] # Top 5
                disease_str = ", ".join(diseases)
                self.ctx.info(f"✅ Found high comorbidity: {disease_str}")
                
            # Check if it's PubMed data (has 'pmid', 'title')
            elif isinstance(first_item, dict) and "pmid" in first_item:
                titles = [f"'{item.get('title', 'Unknown')}'" for item in output[:3]] # Top 3
                self.ctx.info(f"✅ Found articles: {'; '.join(titles)}")

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        self.ctx.info("🤖 Synthesizing answer...")
