import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

def get_driver():
    """
    Creates and returns a Neo4j driver instance using credentials from environment variables.
    """
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, username, password]):
        raise ValueError("Missing Neo4j credentials in environment variables (NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)")

    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        return driver
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Neo4j: {e}")

def close_driver(driver):
    """
    Closes the Neo4j driver instance.
    """
    if driver:
        driver.close()
