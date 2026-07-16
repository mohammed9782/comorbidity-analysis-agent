import pandas as pd
import xml.etree.ElementTree as ET
import pyreadr
import os
from icdmappings import Mapper

def parse_gexf_nodes(gexf_path):
    """Parses GEXF file to extract node ID to ICD code mapping."""
    tree = ET.parse(gexf_path)
    root = tree.getroot()
    # Namespace handling might be needed, usually {http://www.gexf.net/1.3}
    ns = {'g': 'http://www.gexf.net/1.3'}
    
    nodes = {}
    # Find all node elements
    for node in root.findall('.//g:node', ns):
        node_id = node.get('id')
        # Find attributes
        attvalues = node.find('g:attvalues', ns)
        icd_code = None
        descr = None
        if attvalues is not None:
            for attvalue in attvalues.findall('g:attvalue', ns):
                # We assume att1 is icd_code based on inspection
                if attvalue.get('for') == 'att1':
                    icd_code = attvalue.get('value')
                if attvalue.get('for') == 'att5': # LongDescription
                    descr = attvalue.get('value')
        
        if icd_code:
            nodes[int(node_id)] = {'code': icd_code, 'name': descr}
            
    return nodes

def enrich_nodes(nodes_dict):
    """Enriches nodes with prevalence data and standardized names."""
    # 1. Use icd-mappings
    mapper = Mapper()
    
    # 2. Load Prevalence
    prev_path = 'data/1.Prevalence/Prevalence_Sex_Age_Year_ICD.csv'
    if os.path.exists(prev_path):
        df_prev = pd.read_csv(prev_path)
        # Filter for latest year (2014) and aggregate
        df_prev = df_prev[df_prev['year'] == 2014]
        # Mean prevalence across age/sex
        prev_map = df_prev.groupby('icd_code')['p'].mean().to_dict()
    else:
        prev_map = {}

    final_nodes = []
    for nid, data in nodes_dict.items():
        code = data['code']
        name = data['name']
        
        # Try mapper if name is missing or short
        try:
            mapped_name = mapper.map(code)
            if mapped_name:
                name = mapped_name
        except:
            pass
            
        prevalence = prev_map.get(code, 0.0)
        
        final_nodes.append({
            'id': nid, # Keep internal ID for matrix mapping
            'code': code,
            'name': name,
            'prevalence': prevalence
        })
        
    return pd.DataFrame(final_nodes)

def process_edges(nodes_df, matrix_path, rds_path=None):
    """Processes adjacency matrix and optionally RDS for edges."""
    # Create a map of ID -> Code
    id_to_code = dict(zip(nodes_df['id'], nodes_df['code']))
    
    # Read Matrix (Headerless)
    # We assume the matrix rows/cols are ordered by ID 1..1080
    df_matrix = pd.read_csv(matrix_path, header=None, sep=r'\s+|,') # Try flexible separator
    
    # Verify dimensions
    if df_matrix.shape[0] != 1080 or df_matrix.shape[1] != 1080:
        # If separator failed, try comma
        df_matrix = pd.read_csv(matrix_path, header=None, sep=',')
    
    print(f"Matrix shape: {df_matrix.shape}")
    
    edges = []
    # Iterate over upper triangle to avoid duplicates (undirected)
    # But spec says "Relationships are undirected (symmetrical)", Neo4j stores directed.
    # We usually store one direction for undirected semantics or both.
    # Let's store one direction (Source < Target) to save space, logic can handle it.
    
    # Try to read RDS for Risk Ratios
    rr_matrix = None
    if rds_path and os.path.exists(rds_path):
        try:
            rds_data = pyreadr.read_r(rds_path)
            # Assuming the first object is the matrix
            rr_matrix = rds_data[None]
            print("Loaded Risk Ratios from RDS")
        except Exception as e:
            print(f"Could not load RDS: {e}")

    count = 0
    # Using numpy for speed
    mat = df_matrix.values
    
    # Threshold to reduce edges
    THRESHOLD = 0.01 
    
    rows, cols = mat.shape
    for i in range(rows):
        for j in range(i + 1, cols): # Upper triangle
            weight = mat[i, j]
            if weight > THRESHOLD:
                source_id = i + 1 # 1-based ID
                target_id = j + 1
                
                source_code = id_to_code.get(source_id)
                target_code = id_to_code.get(target_id)
                
                if source_code and target_code:
                    risk_ratio = 1.0
                    # If we had RR matrix, we would look it up here
                    # rr_matrix lookup logic would go here
                    
                    edges.append({
                        'source': source_code,
                        'target': target_code,
                        'weight': weight,
                        'risk_ratio': risk_ratio
                    })
                    count += 1
                    
    print(f"Extracted {count} edges")
    return pd.DataFrame(edges)

def main():
    print("Parsing GEXF...")
    gexf_path = 'data/4.Graphs-gexffiles/Graph_Female_ICD_Year_2013.gexf'
    nodes_dict = parse_gexf_nodes(gexf_path)
    print(f"Found {len(nodes_dict)} nodes")
    
    print("Enriching Nodes...")
    nodes_df = enrich_nodes(nodes_dict)
    nodes_df.to_csv('nodes.csv', index=False)
    print("Saved nodes.csv")
    
    print("Processing Edges...")
    matrix_path = 'data/3.AdjacencyMatrices/Adj_Matrix_Female_ICD_year_2013-2014.csv'
    rds_path = 'data/2.ContingencyTables/ICD_ContingencyTables_Female_Final.rds'
    edges_df = process_edges(nodes_df, matrix_path, rds_path)
    edges_df.to_csv('edges.csv', index=False)
    print("Saved edges.csv")

if __name__ == "__main__":
    main()
