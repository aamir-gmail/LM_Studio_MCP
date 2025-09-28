import json
import graphviz

# Input JSON data
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

# Extract nodes and edges
nodes = json_data["directed_graph"]["nodes"]
edges = json_data["directed_graph"]["edges"]

# Create DOT graph
dot = graphviz.Digraph(comment='USDA Organization Structure', engine='dot')
dot.attr(rankdir='LR')  # Left to right layout

# Add nodes
for node in nodes:
    dot.node(node['id'], node['label'])

# Add edges with labels
for edge in edges:
    dot.edge(edge['source'], edge['target'], label=edge['relationship'])

# Render the graph to PNG (HD quality)
dot.render('usda_organization', format='png', cleanup=True)

print("Graphviz DOT code generated:")
print(dot.source)