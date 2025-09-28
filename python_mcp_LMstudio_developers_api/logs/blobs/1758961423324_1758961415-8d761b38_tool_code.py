import json
from graphviz import Graph

# JSON data
data = {
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

# Create Graphviz graph
dot = Graph(comment='USDA Organizational Structure', engine='dot')

# Set global attributes for better appearance
dot.attr(rankdir='TB')  # Top to bottom layout
dot.attr('node', shape='box', style='filled', fillcolor='lightblue')
dot.attr('edge', color='black')

# Add root node (USDA)
dot.node('USDA', 'United States Department of Agriculture', fontsize='16', fontweight='bold')

# Create categories and their nodes
categories = list(data['USDA'].keys())
colors = ['lightcoral', 'lightgreen', 'lightyellow', 'lightpink', 
          'lightcyan', 'lightgray', 'lightgoldenrod', 'lightseagreen']

for i, category in enumerate(categories):
    # Add category node
    dot.node(category, category.replace('_', ' '), fillcolor=colors[i % len(colors)], fontsize='12')
    
    # Connect category to USDA
    dot.edge('USDA', category)
    
    # Add sub-nodes for each organization in the category
    for org in data['USDA'][category]:
        dot.node(org, org, shape='ellipse', fillcolor='white', fontsize='10')
        dot.edge(category, org)

# Render and save graph
dot.render('usda_organizational_structure', format='png', cleanup=True)
print("Graph created successfully as usda_organizational_structure.png")