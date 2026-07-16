import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.db import get_driver, close_driver

def load_data():
    driver = get_driver()
    
    try:
        with driver.session() as session:
            print("Clearing database...")
            session.run("MATCH (n) DETACH DELETE n")
            
            print("Creating constraints...")
            try:
                session.run("CREATE CONSTRAINT disease_code_unique IF NOT EXISTS FOR (d:Disease) REQUIRE d.code IS UNIQUE")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print("  Constraint already exists, skipping...")
                else:
                    raise
            
            print("Loading Nodes...")
            nodes_df = pd.read_csv('nodes.csv')
            # Replace NaN with empty string or 0
            nodes_df = nodes_df.fillna({'name': '', 'prevalence': 0.0})
            nodes_data = nodes_df.to_dict('records')
            
            # Batching
            BATCH_SIZE = 1000
            for i in range(0, len(nodes_data), BATCH_SIZE):
                batch = nodes_data[i:i+BATCH_SIZE]
                session.run("""
                    UNWIND $batch AS row
                    MERGE (d:Disease {code: row.code})
                    SET d.name = row.name,
                        d.prevalence = toFloat(row.prevalence)
                """, batch=batch)
            print(f"Loaded {len(nodes_data)} nodes.")
            
            print("Loading Relationships...")
            edges_df = pd.read_csv('edges.csv')
            edges_data = edges_df.to_dict('records')
            
            for i in range(0, len(edges_data), BATCH_SIZE):
                batch = edges_data[i:i+BATCH_SIZE]
                session.run("""
                    UNWIND $batch AS row
                    MATCH (a:Disease {code: row.source})
                    MATCH (b:Disease {code: row.target})
                    MERGE (a)-[r:CO_OCCURS_WITH]-(b)
                    SET r.weight = toFloat(row.weight),
                        r.risk_ratio = toFloat(row.risk_ratio)
                """, batch=batch)
            print(f"Loaded {len(edges_data)} relationships.")
            
    except Exception as e:
        print(f"Error loading data: {e}")
        raise
    finally:
        close_driver(driver)

if __name__ == "__main__":
    load_data()
