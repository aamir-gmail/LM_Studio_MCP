import graphviz

# Create a directed graph with enhanced styling
dot = graphviz.Digraph('USDA_Organizational_Structure', comment='USDA Organizational Structure')

# Set graph attributes for better appearance
dot.attr(rankdir='LR')  # Left to right layout
dot.attr(splines='curved')  # Curved edges for better visual flow
dot.attr(fontsize='12')
dot.attr(bgcolor='white')

# Define colors for different categories
colors = {
    'Research_Statistics_Analysis': '#FF6B6B',
    'Food_Safety_Nutrition': '#4ECDC4',
    'Marketing_Trade': '#45B7D1',
    'Farming_Risk_Management': '#96CEB4',
    'Animal_Plant_Health': '#FFEAA7',
    'Forests_Conservation': '#DDA0DD',
    'Rural_Development': '#98D8C8',
    'Support_Offices': '#F7DC6F'
}

# Add central USDA node
dot.node('USDA', 'United States Department of Agriculture', 
         shape='ellipse', style='filled', fillcolor='#2C3E50', fontcolor='white', fontsize='14')

# Define the structure from JSON data
usda_structure = {
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

# Add category clusters with their agencies
for category, agencies in usda_structure.items():
    # Create a subgraph for each category
    with dot.subgraph(name=f'cluster_{category}') as c:
        c.attr(label=category.replace('_', ' ').title(), 
               style='filled', 
               fillcolor=colors[category], 
               color=colors[category],
               fontcolor='white',
               fontsize='12')
        
        # Add agencies to the category cluster
        for agency in agencies:
            c.node(agency, agency, shape='box', style='rounded,filled', fillcolor='white', fontcolor='#333333')
            
        # Connect category cluster to USDA
        c.attr('node', shape='circle', fillcolor=colors[category], style='filled')
        c.node(category.replace('_', ' ').title(), category.replace('_', ' ').title(), 
               style='filled', fillcolor=colors[category], fontcolor='white')

# Connect USDA to each category cluster
for category in usda_structure.keys():
    dot.edge('USDA', category.replace('_', ' ').title())

# Add connections between agencies within the same category (optional - for better visualization)
for category, agencies in usda_structure.items():
    if len(agencies) > 1:
        # Connect first agency to others in cluster
        for i in range(1, len(agencies)):
            dot.edge(agencies[0], agencies[i])

# Render the graph
dot.render('usda_organizational_structure', format='png', cleanup=True)
print("Graph generated successfully!")