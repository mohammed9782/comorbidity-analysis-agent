import os
import httpx
import xmltodict
from typing import List, Dict, Any
from src.utils.db import get_driver, close_driver

# --- Neo4j Tool ---

def query_neo4j(icd_code: str, threshold: float = 0.01) -> List[Dict[str, Any]]:
    """
    Queries Neo4j for diseases co-occurring with the given ICD code.
    Returns a list of dictionaries with related disease info.
    """
    driver = get_driver()
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (a:Disease {code: $code})-[r:CO_OCCURS_WITH]-(b:Disease)
                WHERE r.weight > $threshold
                RETURN b.code as code, b.name as name, r.weight as weight, r.risk_ratio as risk_ratio
                ORDER BY r.weight DESC
                LIMIT 10
            """, code=icd_code, threshold=threshold)
            
            return [record.data() for record in result]
    except Exception as e:
        print(f"Neo4j Query Error: {e}")
        return []
    finally:
        close_driver(driver)

# --- PubMed Tool ---

async def search_pubmed(query: str, email: str = None, api_key: str = None) -> List[Dict[str, str]]:
    """
    Searches PubMed for the given query and returns top abstracts.
    Uses NCBI E-utilities (esearch + efetch).
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # Use env vars if not provided
    if not email:
        email = os.getenv("PUBMED_EMAIL")
    if not api_key:
        api_key = os.getenv("PUBMED_API_KEY")
        
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": 3,
        "email": email,
        "api_key": api_key
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. ESearch
            resp = await client.get(f"{base_url}/esearch.fcgi", params=params)
            resp.raise_for_status()
            data = resp.json()
            
            id_list = data.get("esearchresult", {}).get("idlist", [])
            if not id_list:
                return []
            
            # 2. EFetch
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "xml",
                "email": email,
                "api_key": api_key
            }
            
            resp = await client.get(f"{base_url}/efetch.fcgi", params=fetch_params)
            resp.raise_for_status()
            
            # Parse XML
            xml_data = xmltodict.parse(resp.text)
            articles = []
            
            # Handle single vs multiple articles in XML structure
            pubmed_articles = xml_data.get("PubmedArticleSet", {}).get("PubmedArticle", [])
            if isinstance(pubmed_articles, dict):
                pubmed_articles = [pubmed_articles]
                
            for article in pubmed_articles:
                try:
                    medline = article.get("MedlineCitation", {})
                    article_data = medline.get("Article", {})
                    
                    title = article_data.get("ArticleTitle", "No Title")
                    abstract_data = article_data.get("Abstract", {}).get("AbstractText", "")
                    
                    # AbstractText can be a list or string
                    abstract = ""
                    if isinstance(abstract_data, list):
                        abstract = " ".join([item.get("#text", "") if isinstance(item, dict) else str(item) for item in abstract_data])
                    elif isinstance(abstract_data, dict):
                        abstract = abstract_data.get("#text", "")
                    else:
                        abstract = str(abstract_data)
                        
                    pub_date = article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
                    year = pub_date.get("Year", "Unknown")
                    
                    articles.append({
                        "title": title,
                        "abstract": abstract,
                        "year": year,
                        "pmid": medline.get("PMID", {}).get("#text", "")
                    })
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
                    
            return articles
            
        except Exception as e:
            print(f"PubMed API Error: {e}")
            return []
