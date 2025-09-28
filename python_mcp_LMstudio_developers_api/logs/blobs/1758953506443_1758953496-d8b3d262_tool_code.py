import json
from graphviz import Graph

# Define the JSON data
data = {
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

# Create the graph
dot = Graph(comment='USDA Organization Chart', directed=True)

# Set graph attributes for better visualization
dot.attr(rankdir='LR')  # Left to right layout
dot.attr(splines='curved')
dot.attr(fontsize='12')

# Add nodes
for node in data['directed_graph']['nodes']:
    dot.node(node['id'], node['label'])

# Add edges with relationship labels
for edge in data['directed_graph']['edges']:
    dot.edge(edge['source'], edge['target'], label=edge['relationship'])

# Render the graph to PNG
dot.render('usda_organization', format='png', cleanup=True)

print("Graphviz visualization saved as 'usda_organization.png'")