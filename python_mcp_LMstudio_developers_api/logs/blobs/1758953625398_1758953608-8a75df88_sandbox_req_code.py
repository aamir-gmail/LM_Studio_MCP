import json

# Define the JSON data for USDA organization structure
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

# Generate DOT code for Graphviz
dot_code = """digraph USDA_Organization {
    rankdir=LR;
    splines=curved;
    fontsize=12;
    bgcolor=white;
    
    // Node definitions with custom styling
    node [shape=box, style=filled, fillcolor=lightblue, fontname="Arial", fontsize=10];
    
    // All nodes
"""

for node in data['directed_graph']['nodes']:
    dot_code += f'    "{node["id"]}" [label="{node["label"]}"];\n'

dot_code += "\n    // Edge definitions with relationship labels\n"

for edge in data['directed_graph']['edges']:
    dot_code += f'    "{edge["source"]}" -> "{edge["target"]}" [label="{edge["relationship"]}", fontname="Arial", fontsize=9];\n'

dot_code += "}\n"

# Save DOT file
with open('usda_organization.dot', 'w') as f:
    f.write(dot_code)

print("DOT code generated successfully!")
print("\nHere's the complete DOT code that would generate the USDA organizational chart:")
print("="*60)
print(dot_code)
print("="*60)
print("\nTo visualize this graph, you would need to:")
print("1. Install Graphviz on your system")
print("2. Run: dot -Tpng usda_organization.dot -o usda_organization.png")

# Also provide a simple text representation
print("\n" + "="*50)
print("TEXT REPRESENTATION OF THE ORGANIZATION CHART:")
print("="*50)
print("USDA (United States Department of Agriculture)")
print("    ↓ operates")
print("AMS → Agricultural Marketing Service")
print("    ↓ operates") 
print("FNS → Food and Nutrition Service")
print("    ↓ operates")
print("APHIS → Animal and Plant Health Inspection Service")
print("    ↓ operates")
print("FSIS → Food Safety and Inspection Service")
print("    ↓ operates")
print("ARS → Agricultural Research Service")
print("    ↓ operates")
print("NASS → National Agricultural Statistics Service")
print("    ↓ operates")
print("FAS → Foreign Agricultural Service")
print("    ↓ operates")
print("RDA → Rural Development Administration")
print("    ↓ operates")
print("FSA → Farm Service Agency")
print("    ↓ operates")
print("NRCS → Natural Resources Conservation Service")
print("    ↓ operates")
print("CCS → Commodity Credit Corporation")
print("    ↓ operates")
print("GIPSA → Grain Inspection, Packers and Stockyards Administration")
print("    ↓ operates")
print("RUS → Rural Utilities Service")
print("    ↓ operates")
print("OS → Office of the Secretary")
print("    ↓ operates")
print("OCE → Office of the Chief Economist")