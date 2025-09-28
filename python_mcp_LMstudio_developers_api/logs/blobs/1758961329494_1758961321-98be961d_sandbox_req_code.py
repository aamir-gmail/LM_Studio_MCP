import json
from graphviz import Graph

# JSON data
usda_data = {
"USDA": {
"Research_Statistics_Analysis": [
"Agricultural Research Service",
"Economic Research Service",
"National Agricultural Statistics Service",
"National Institute of Food and Agriculture",
"National Agricultural Library",
"World Agricultural Outlook Board"
],
"Food_Safety_Nutrition": [
"Food and Nutrition Service",
"Food Safety and Inspection Service"
],
"Marketing_Trade": [
"Agricultural Marketing Service",
"Foreign Agricultural Service",
"Commodity Credit Corporation"
],
"Farming_Risk_Management": [
"Farm Service Agency",
"Federal Crop Insurance Corporation"
],
"Animal_Plant_Health": [
"Animal and Plant Health Inspection Service"
],
"Forests_Conservation": [
"Forest Service",
"Natural Resources Conservation Service"
],
"Rural_Development": [
"Rural Business-Cooperative Service",
"Rural Development Administration",
"Rural Housing Service",
"Rural Utilities Service"
],
"Support_Offices": [
"Office of the Secretary of Agriculture",
"Office of Advocacy and Outreach",
"Office of the Chief Financial Officer",
"Office of Energy and Environmental Policy",
"Office of Energy Policy and New Uses",
"Office of Environmental Quality",
"Office of Information Resources Management",
"Office of Inspector General",
"Office of Operations",
"Office of Procurement and Property Management",
"Office of Transportation"
]
}
}

# Create a directed graph
dot = Graph(comment='USDA Organizational Structure', engine='dot')
dot.attr(rankdir='TB')  # Top to bottom layout

# Add the main USDA node
dot.node('USDA', 'USDA', shape='box', style='filled', fillcolor='#4A90E2', fontcolor='white')

# Create clusters for each category
for category, agencies in usda_data['USDA'].items():
    # Create a subgraph (cluster) for each category
    with dot.subgraph(name=f'cluster_{category}') as c:
        c.attr(label=category.replace('_', ' '), style='filled', fillcolor='#f0f8ff')
        c.attr(penwidth='2')  # Border width
        
        # Add nodes for each agency in the category
        for agency in agencies:
            c.node(agency, agency, shape='ellipse', style='filled', fillcolor='#7FDBFF')
        
        # Connect category label to its agencies
        if len(agencies) > 0:
            c.edge(category.replace('_', ' '), agencies[0], style='invis')

# Connect USDA to each category cluster
categories = list(usda_data['USDA'].keys())
for i, category in enumerate(categories):
    dot.edge('USDA', category.replace('_', ' '), style='bold')

# Add connections between related nodes (if any)
# For this visualization, we'll focus on the hierarchical structure

# Render the graph
dot.render('./usda_organizational_structure.gv', view=False)

# Generate PNG image
dot.format = 'png'
dot.render('./usda_organizational_structure', view=True)

print("Graph has been created and saved as usda_organizational_structure.png")