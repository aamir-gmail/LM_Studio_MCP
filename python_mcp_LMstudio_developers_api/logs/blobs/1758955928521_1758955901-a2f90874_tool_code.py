import json
from graphviz import Graph

# Cleaned JSON data without comments
data = {
  "nodes": [
    {
      "id": "USDA",
      "type": "Department",
      "properties": {
        "name": "United States Department of Agriculture"
      }
    },
    {
      "id": "Farm_Production_Conservation",
      "type": "MissionArea",
      "properties": { "name": "Farm Production and Conservation" }
    },
    {
      "id": "Food_Nutrition_Consumer_Services",
      "type": "MissionArea",
      "properties": { "name": "Food, Nutrition, and Consumer Services" }
    },
    {
      "id": "Food_Safety",
      "type": "MissionArea",
      "properties": { "name": "Food Safety" }
    },
    {
      "id": "Marketing_Regulatory_Programs",
      "type": "MissionArea",
      "properties": { "name": "Marketing and Regulatory Programs" }
    },
    {
      "id": "Natural_Resources_Environment",
      "type": "MissionArea",
      "properties": { "name": "Natural Resources and Environment" }
    },
    {
      "id": "Research_Education_Economics",
      "type": "MissionArea",
      "properties": { "name": "Research, Education, and Economics" }
    },
    {
      "id": "Rural_Development",
      "type": "MissionArea",
      "properties": { "name": "Rural Development" }
    },
    {
      "id": "Trade_Foreign_Affairs",
      "type":"MissionArea",
      "properties":{"name":"Trade and Foreign Agricultural Affairs"}
    },

    /* Agencies under Farm Production & Conservation */
    {"id":"FSA","type":"Agency","properties":{"name":"Farm Service Agency"}},
    {"id":"NRCS","type":"Agency","properties":{"name":"Natural Resources Conservation Service"}},
    {"id":"RMA","type":"Agency","properties":{"name":"Risk Management Agency"}},
    {"id":"CCC","type":"Agency","properties":{"name":"Commodity Credit Corporation"}},

    /* Agencies under Food, Nutrition, and Consumer Services */
    {"id":"FNS","type":"Agency","properties":{"name":"Food and Nutrition Service"}},
    {"id":"CNPP","type":"Agency","properties":{"name":"Center for Nutrition Policy and Promotion"}},

    /* Agencies under Food Safety */
    {"id":"FSIS","type":"Agency","properties":{"name":"Food Safety and Inspection Service"}},

    /* Agencies under Marketing & Regulatory Programs */
    {"id":"AMS","type":"Agency","properties":{"name":"Agricultural Marketing Service"}},
    {"id":"APHIS","type":"Agency","properties":{"name":"Animal and Plant Health Inspection Service"}},
    {"id":"GIPSA","type":"Agency","properties":{"name":"Grain Inspection, Packers & Stockyards Administration"}},

    /* Agencies under Natural Resources & Environment */
    {"id":"FS","type":"Agency","properties":{"name":"Forest Service"}},

    /* Agencies under Research, Education & Economics */
    {"id":"ARS","type":"Agency","properties":{"name":"Agricultural Research Service"}},
    {"id":"ERS","type":"Agency","properties":{"name":"Economic Research Service"}},
    {"id":"NASS","type":"Agency","properties":{"name":"National Agricultural Statistics Service"}},
    {"id":"NIFA","type":"Agency","properties":{"name":"National Institute of Food and Agriculture"}},
    {"id":"NAL","type":"Agency","properties":{"name":"National Agricultural Library"}},

    /* Agencies under Rural Development */
    {"id":"RUS","type":"Agency","properties":{"name":"Rural Utilities Service"}},
    {"id":"RHS","type":"Agency","properties":{"name":"Rural Housing Service"}},
    {"id":"RBS","type":"Agency","properties":{"name":"Rural Business-Cooperative Service"}},

    /* Agencies under Trade & Foreign Affairs */
    {"id":"FAS","type":"Agency","properties":{"name":"Foreign Agricultural Service"}},

   /* Additional Offices */
   {"id":"OAO", "type":"Office", "properties":{"name":"Office of Advocacy and Outreach"}},
   {"id":"OEEP", "type":"Office", "properties":{"name":"Office of Energy and Environmental Policy"}},
   {"id":"OIG", "type":"Office", "properties":{"name":"Office of Inspector General"}}
  ],

  'edges': [
     /* Connect USDA to Mission Areas */
     {'source':'USDA','target':'Farm_Production_Conservation','type':'has_mission_area'},
     {'source':'USDA','target':'Food_Nutrition_Consumer_Services','type':'has_mission_area'},
     {'source':'USDA','target':'Food_Safety','type':'has_mission_area'},
     {'source':'USDA','target':'Marketing_Regulatory_Programs','type':'has_mission_area'},
     {'source':'USDA','target':'Natural_Resources_Environment','type':'has_mission_area'},
     {'source':'USDA','target':'Research_Education_Economics','type':'has_mission_area'},
     {'source':'USDA','target':'Rural_Development','type':'has_mission_area'},
     {'source':'USDA','target':'Trade_Foreign_Affairs','type':'has_mission_area'},

     /* Connect Mission Areas to their agencies */
     {'source':'Farm_Production_Conservation','target':'FSA','type':'oversees'},
     {'source':'Farm_Production_Conservation','target':'NRCS','type':'oversees'},
     {'source':'Farm_Production_Conservation','target':'RMA','type':'oversees'},
     {'source':'Farm_Production_Conservation','target':'CCC','type':'oversees'},

     {'source':'Food_Nutrition_Consumer_Services','target':'FNS','type':'oversees'},
     {'source':'Food_Nutrition_Consumer_Services','target':'CNPP','type':'oversees'},

     {'source':'Food_Safety','target':'FSIS','type':'oversees'},

     {'source':'Marketing_Regulatory_Programs','target':'AMS','type':'oversees'},
     {'source':'Marketing_Regulatory_Programs','target':'APHIS','type':'oversees'},
     {'source':'Marketing_Regulatory_Programs','target':'GIPSA','type':'oversees'},

     {'source':'Natural_Resources_Environment','target':'FS','type':'oversees'},

     {'source':'Research_Education_Economics','target':'ARS','type':'oversees'},
     {'source':'Research_Education_Economics','target':'ERS','type':'oversees'},
     {'source':'Research_Education_Economics','target':'NASS','type':'oversees'},
     {'source':'Research_Education_Economics','target':'NIFA','type':'oversees'},
     {'source':'Research_Education_Economics','target':'NAL','type':'oversees'},

     {'source':'Rural_Development','target':'RUS','type':'oversees'},
     {'source':'Rural_Development','target':'RHS','type':'oversees'},
     {'source':'Rural_Development','target':'RBS','type':'oversees'},

     {'source':'Trade_Foreign_Affairs','target':'FAS','type':'oversees'},

   /* Additional Offices connected directly to USDA */
   {'source':'USDA','target':'OAO','type':'has_office'},
   {'source':'USDA','target':'OEEP','type':'has_office'},
   {'source':'USDA','target':'OIG','type':'has_office'}
 ]
}

# Create a directed graph
dot = Graph(comment='USDA Organizational Structure', engine='dot')
dot.attr(rankdir='TB')  # Top to bottom layout

# Define styles for different node types
node_styles = {
    'Department': {'style': 'filled', 'color': '#4A90E2', 'fontcolor': 'white'},
    'MissionArea': {'style': 'filled', 'color': '#50C878', 'fontcolor': 'white'},
    'Agency': {'style': 'filled', 'color': '#FFA500', 'fontcolor': 'black'},
    'Office': {'style': 'filled', 'color': '#9370DB', 'fontcolor': 'white'}
}

# Add nodes to the graph
for node in data['nodes']:
    node_id = node['id']
    node_type = node['type']
    node_name = node['properties']['name']
    
    # Set up styling based on type
    style = node_styles.get(node_type, {'style': 'filled', 'color': '#D3D3D3'})
    
    dot.node(node_id, label=f"{node_name}\n({node_type})", **style)

# Add edges to the graph
for edge in data['edges']:
    source = edge['source']
    target = edge['target']
    edge_type = edge['type']
    
    # Set edge style based on relationship type
    if edge_type == 'has_mission_area':
        dot.edge(source, target, label='has', color='#4A90E2')
    elif edge_type == 'oversees':
        dot.edge(source, target, label='oversees', color='#FF6347')
    elif edge_type == 'has_office':
        dot.edge(source, target, label='has', color='#8B4513')

# Render the graph
dot.render('usda_organizational_structure', format='png', cleanup=True)
print("USDA organizational structure visualization created successfully!")