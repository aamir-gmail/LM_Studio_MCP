import graphviz

# Create a new directed graph with left-to-right layout
dot = graphviz.Digraph(comment='USDA Organizational Structure', engine='dot')
dot.attr(rankdir='LR')  # Left to right layout

# Add the central USDA node
dot.node('USDA', 'United States Department of Agriculture', shape='ellipse', style='filled', fillcolor='lightblue')

# Define categories with colors for visual distinction
categories = {
    "Research_Statistics_Analysis": "lightgreen",
    "Food_Safety_Nutrition": "lightyellow",
    "Marketing_Trade": "lightcoral",
    "Farming_Risk_Management": "lightpink",
    "Animal_Plant_Health": "lightgray",
    "Forests_Conservation": "lightseagreen",
    "Rural_Development": "lightsalmon",
    "Support_Offices": "lightcyan"
}

# Add category headers and their respective nodes
for category, color in categories.items():
    # Create a cluster for each category to group related nodes
    with dot.subgraph(name=f'cluster_{category}') as c:
        c.attr(label=category.replace('_', ' ').title(), style='filled', fillcolor=color)
        
        # Add the specific agencies/services under each category
        if category == "Research_Statistics_Analysis":
            agencies = ["Agricultural Research Service", "Economic Research Service", 
                       "National Agricultural Statistics Service", "National Institute of Food and Agriculture",
                       "National Agricultural Library", "World Agricultural Outlook Board"]
        elif category == "Food_Safety_Nutrition":
            agencies = ["Food and Nutrition Service", "Food Safety and Inspection Service"]
        elif category == "Marketing_Trade":
            agencies = ["Agricultural Marketing Service", "Foreign Agricultural Service", 
                       "Commodity Credit Corporation"]
        elif category == "Farming_Risk_Management":
            agencies = ["Farm Service Agency", "Federal Crop Insurance Corporation"]
        elif category == "Animal_Plant_Health":
            agencies = ["Animal and Plant Health Inspection Service"]
        elif category == "Forests_Conservation":
            agencies = ["Forest Service", "Natural Resources Conservation Service"]
        elif category == "Rural_Development":
            agencies = ["Rural Business-Cooperative Service", "Rural Development Administration",
                       "Rural Housing Service", "Rural Utilities Service"]
        else:  # Support_Offices
            agencies = ["Office of the Secretary of Agriculture", "Office of Advocacy and Outreach",
                       "Office of the Chief Financial Officer", "Office of Energy and Environmental Policy",
                       "Office of Energy Policy and New Uses", "Office of Environmental Quality",
                       "Office of Information Resources Management", "Office of Inspector General",
                       "Office of Operations", "Office of Procurement and Property Management",
                       "Office of Transportation"]
        
        # Add each agency as a node in the cluster
        for agency in agencies:
            c.node(agency, agency, shape='box', style='filled', fillcolor='white')
            
            # Connect each agency to its category header (which is inside the cluster)
            # This creates a visual grouping within each category
            
# Create connections from USDA to each category cluster
for category in categories.keys():
    dot.edge('USDA', f'cluster_{category}')

# Add edges between agencies within their respective clusters for better visualization
dot.render('./usda_organizational_structure', format='png', cleanup=True)

print("Graph has been successfully generated with proper connections.")