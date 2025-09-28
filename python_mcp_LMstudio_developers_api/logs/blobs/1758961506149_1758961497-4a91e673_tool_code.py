import graphviz

# Create a new directed graph with horizontal layout
dot = graphviz.Digraph(comment='USDA Organizational Structure', engine='dot')
dot.attr(rankdir='LR')  # Left to right layout

# Add the main USDA node
dot.node('USDA', 'United States Department of Agriculture', shape='box', style='filled', fillcolor='lightblue')

# Define categories and their nodes with colors for distinction
categories = {
    "Research_Statistics_Analysis": {
        "color": "lightgreen",
        "nodes": [
            "Agricultural Research Service",
            "Economic Research Service", 
            "National Agricultural Statistics Service",
            "National Institute of Food and Agriculture",
            "National Agricultural Library",
            "World Agricultural Outlook Board"
        ]
    },
    "Food_Safety_Nutrition": {
        "color": "lightyellow",
        "nodes": [
            "Food and Nutrition Service",
            "Food Safety and Inspection Service"
        ]
    },
    "Marketing_Trade": {
        "color": "lightcoral",
        "nodes": [
            "Agricultural Marketing Service",
            "Foreign Agricultural Service",
            "Commodity Credit Corporation"
        ]
    },
    "Farming_Risk_Management": {
        "color": "lightpink",
        "nodes": [
            "Farm Service Agency",
            "Federal Crop Insurance Corporation"
        ]
    },
    "Animal_Plant_Health": {
        "color": "lightgray",
        "nodes": [
            "Animal and Plant Health Inspection Service"
        ]
    },
    "Forests_Conservation": {
        "color": "lightseagreen",
        "nodes": [
            "Forest Service",
            "Natural Resources Conservation Service"
        ]
    },
    "Rural_Development": {
        "color": "lightsteelblue",
        "nodes": [
            "Rural Business-Cooperative Service",
            "Rural Development Administration",
            "Rural Housing Service",
            "Rural Utilities Service"
        ]
    },
    "Support_Offices": {
        "color": "lightgoldenrod",
        "nodes": [
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

# Add category headers and their nodes
for category, data in categories.items():
    # Create a cluster for each category to group related nodes
    with dot.subgraph(name=f'cluster_{category}') as c:
        c.attr(style='filled', color=data['color'], label=category.replace('_', ' '))
        for node in data['nodes']:
            c.node(node, node, shape='ellipse')
    
# Connect USDA to each category cluster
for category in categories.keys():
    dot.edge('USDA', f'cluster_{category}', style='invis')

# Add connections between nodes within the same cluster (optional - makes it clearer)
for category, data in categories.items():
    with dot.subgraph(name=f'cluster_{category}') as c:
        # Connect all nodes within a category to each other for better visual grouping
        for i in range(len(data['nodes'])-1):
            if len(data['nodes']) > 1:
                c.edge(data['nodes'][i], data['nodes'][i+1], style='invis')

# Render the graph
dot.render('usda_organizational_structure', format='png', cleanup=True)
print("Graph rendered successfully")