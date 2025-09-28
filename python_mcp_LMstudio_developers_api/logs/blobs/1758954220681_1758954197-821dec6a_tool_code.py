import json
from graphviz import Graph

# JSON data provided by user
json_data = {
    "directed_graph": {
        "nodes": [
            {"id": "USDA", "label": "United States Department of Agriculture"},
            {"id": "AMS", "label": "Agricultural Marketing Service"},
            {"id": "FNS", "label": "Food and Nutrition Service"},
            {"id": "APHIS", "label": "Animal and Plant Health Inspection Service"},
            {"id": "FSIS", "label": "Food Safety and Inspection Service"},
            {"id": "ARS", "label": "Agricultural Research Service"},
            {"id": "NASS", "label": "National Agricultural Statistics Service"},
            {"id": "FAS", "label": "Foreign Agricultural Service"},
            {"id": "RDA", "label": "Rural Development Administration"},
            {"id": "FSA", "label": "Farm Service Agency"},
            {"id": "NRCS", "label": "Natural Resources Conservation Service"},
            {"id": "CCS", "label": "Commodity Credit Corporation"},
            {"id": "GIPSA", "label": "Grain Inspection, Packers and Stockyards Administration"},
            {"id": "RUS", "label": "Rural Utilities Service"},
            {"id": "OS", "label": "Office of the Secretary"},
            {"id": "OCE", "label": "Office of the Chief Economist"}
        ],
        "edges": [
            {"source": "USDA", "target": "AMS", "relationship": "operates"},
            {"source": "USDA", "target": "FNS", "relationship": "operates"},
            {"source": "USDA", "target": "APHIS", "relationship": "operates"},
            {"source": "USDA", "target": "FSIS", "relationship": "operates"},
            {"source": "USDA", "target": "ARS", "relationship": "operates"},
            {"source": "USDA", "target": "NASS", "relationship": "operates"},
            {"source": "USDA", "target": "FAS", "relationship": "operates"},
            {"source": "USDA", "target": "RDA", "relationship": "operates"},
            {"source": "USDA", "target": "FSA", "relationship": "operates"},
            {"source": "USDA", "target": "NRCS", "relationship": "operates"},
            {"source": "USDA", "target": "CCS", "relationship": "operates"},
            {"source": "USDA", "target": "GIPSA", "relationship": "operates"},
            {"source": "USDA", "target": "RUS", "relationship": "operates"},
            {"source": "USDA", "target": "OS", "relationship": "operates"},
            {"source": "USDA", "target": "OCE", "relationship": "operates"}
        ]
    }
}

# Create a directed graph with enhanced styling
dot = Graph(comment='USDA Organization Structure')
dot.attr(rankdir='LR')  # Left to right layout
dot.attr(bgcolor='white')
dot.attr(fontsize='12')

# Define styles for different node types
dot.attr('node', style='filled', fillcolor='lightblue', fontname='Arial', fontsize='10')
dot.attr('edge', fontname='Arial', fontsize='9', color='darkblue')

# Add nodes with enhanced styling
for node in json_data['directed_graph']['nodes']:
    if node['id'] == 'USDA':
        # Make USDA more prominent
        dot.node(node['id'], node['label'], fillcolor='lightcoral', style='filled,rounded')
    else:
        # Regular agency nodes
        dot.node(node['id'], node['label'])

# Add edges with enhanced styling
for edge in json_data['directed_graph']['edges']:
    dot.edge(edge['source'], edge['target'], label=edge['relationship'], color='darkblue', 
             fontcolor='darkblue', arrowsize='0.8')

# Set overall graph attributes for better appearance
dot.attr(ranksep='1.2')  # Increase spacing between ranks
dot.attr(nodesep='0.5')  # Increase spacing between nodes

# Render the enhanced graph to PNG
dot.render('usda_organization_enhanced', format='png', cleanup=True)

print("Enhanced Graphviz visualization created successfully!")