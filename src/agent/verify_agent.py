import asyncio
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.agent.graph import app

load_dotenv()

async def verify_agent():
    query = "I have hypertension (I10). What else am I at risk for?"
    print(f"Testing Query: {query}")
    
    initial_state = {
        "user_query": query,
        "messages": [],
        "entities": [],
        "graph_data": [],
        "evidence": [],
        "exploration_mode": False
    }
    
    try:
        result = await app.ainvoke(initial_state)
        
        print("\n--- Entities ---")
        print(result["entities"])
        
        print("\n--- Graph Data (Top 3) ---")
        for item in result["graph_data"][:3]:
            print(f"{item['code']} ({item['name']}): Weight {item['weight']}")
            
        print("\n--- Evidence (Top 3) ---")
        for item in result["evidence"][:3]:
            print(f"Title: {item['title']}")
            print(f"Context: {item.get('context', '')}")
            print("-" * 20)
            
        print("\n--- Final Answer ---")
        print(result["messages"][-1].content)
        
    except Exception as e:
        print(f"Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_agent())
