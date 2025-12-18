import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.db import get_driver, close_driver

def verify_data():
    driver = get_driver()
    try:
        with driver.session() as session:
            # 1. Count Nodes
            result = session.run("MATCH (n:Disease) RETURN count(n) as count")
            node_count = result.single()['count']
            print(f"Node Count: {node_count}")
            assert node_count > 0, "Node count should be > 0"
            
            # 2. Count Relationships
            result = session.run("MATCH ()-[r:CO_OCCURS_WITH]->() RETURN count(r) as count")
            edge_count = result.single()['count']
            print(f"Edge Count: {edge_count}")
            assert edge_count > 0, "Edge count should be > 0"
            
            # 3. Sample Path
            print("\nSample Path:")
            result = session.run("""
                MATCH (a:Disease)-[r:CO_OCCURS_WITH]-(b:Disease)
                RETURN a.code, a.name, r.weight, b.code, b.name
                LIMIT 5
            """)
            for record in result:
                print(f"{record['a.code']} ({record['a.name']}) --[{record['r.weight']}]--> {record['b.code']} ({record['b.name']})")
                
            print("\nVerification Passed!")
            
    except Exception as e:
        print(f"Verification Failed: {e}")
        raise
    finally:
        close_driver(driver)

if __name__ == "__main__":
    verify_data()
