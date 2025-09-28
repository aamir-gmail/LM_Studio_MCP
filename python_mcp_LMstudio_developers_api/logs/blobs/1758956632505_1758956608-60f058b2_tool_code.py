import json
import re

# Original JSON with errors
json_data = '''{
"nodes": [
{
"id": "USDA",
"type": "Department",
"properties": {
"name": "United States Department of Agriculture",
"description": "Federal executive department responsible for agriculture, food, forestry, rural development, and nutrition programs."
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
,"type":"MissionArea","properties":{"name":"Trade and Foreign Agricultural Affairs"}}
,
{
"id":"FSA","type":"Agency","properties":{"name":"Farm Service Agency","description":"Provides farm programs, disaster assistance, and direct support to farmers."}},
{"id":"NRCS","type":"Agency","properties":{"name":"Natural Resources Conservation Service","description":"Helps farmers conserve soil, water, and natural resources."}},
{"id":"RMA","type":"Agency","properties":{"name":"Risk Management Agency","description":"Manages crop insurance programs to reduce risk for farmers."}},
{"id":"CCC","type":"Agency","properties":{"name":"Commodity Credit Corporation","description":"Provides financial instruments to stabilize and support farm income."}},
{"id":"FNS","type":"Agency","properties":{"name":"Food and Nutrition Service","description":"Administers SNAP (food stamps), WIC, and school meal programs."}},
{"id":"CNPP","type":"Agency","properties":{"name":"Center for Nutrition Policy and Promotion","description":"Develops dietary guidelines and nutrition education."}},
{"id":"FSIS","type":"Agency","properties":{"name":"Food Safety and Inspection Service","description":"Ensures safety of meat, poultry, and processed egg products through inspections."}},
{"id":"AMS","type":"Agency","properties":{"name":"Agricultural Marketing Service","description":"Oversees commodity standards, grading, fair trade practices, marketing orders."}},
{"id":"APHIS","type":"Agency","properties":{"name":"Animal and Plant Health Inspection Service","description":"Protects U.S. agriculture from pests/diseases; regulates animal/plant health imports/exports."}},
{"id":"GIPSA","type":"Agency","properties":{"name":"Grain Inspection, Packers & Stockyards Administration","description":"Oversees grain quality standards and fair competition in livestock/meat markets."}},
{"id ":"FS "," type ":"Agency "," properties ":{" name ":"Forest Service "," description ":"Manages national forests , grasslands , forestry research , wildfire prevention ."}},
{" id ":"ARS "," type ":"Agency "," properties ":{" name ":"Agricultural Research Service "," description ":"Conducts scientific agricultural research to improve farming practices ."}},
{" id ":"ERS "," type ":"Agency "," properties ":{" name ":"Economic Research Service "," description ":"Provides economic analysis of agriculture / food systems ."}},
{" id ":"NASS "," type ":"Agency "," properties ":{" name ":"National Agricultural Statistics Service "," description ":"Collects / publishes agricultural data nationwide ."}},
{" id ":"NIFA "," type ":"Agency "," properties ":{" name ":"National Institute of Food and Agriculture "," description ":"Funds research , education programs at universities / colleges through land - grant system ."}},
{" id ":"NAL "," type ":"Agency "," properties ":{" name ":"National Agricultural Library "," description ":"Largest agricultural library providing information resources globally ."}},
{  ," id  ":  ," RUS  ",  ," type  ":  ," Agency  ",  ," properties  ": {" name  ":  ," Rural Utilities Service  ",   ," description  ":   ," Finances rural infrastructure like broadband internet , electricity , water systems ."}} ,
{," id   ":," RHS   ",," type   ":," Agency   ",," properties   ": {" name   ":," Rural Housing Service   ",," description   ":," Provides loans / grants for affordable housing in rural areas. "} },
{," id   ":," RBS   ",," type   ":," Agency   ",," properties   ": {" name   ":," Rural Business-Cooperative Service   ",," description   ":," Supports rural business development & cooperatives with funding programs. "} },
{," id   ":," FAS   ",," type   ":," Agency   ",," properties   ": {" name   ":," Foreign Agricultural Service   ",," description   ":," Manages international trade policy for U.S agriculture ; oversees global food aid programs ; promotes exports abroad. "} },
{," id   ":," OAO   ",," type   ":," Office   ",," properties   ": {" name   ":," Office of Advocacy and Outreach   ",," description   ":," Provides outreach to underserved farmers/minority groups in agriculture. "} },
{," id   ":," OEEP   ",," type   ":," Office   ",," properties   ": {" name   ":," Office of Energy and Environmental Policy   ",," description   ":," Develops policies related to renewable energy & environmental sustainability in agriculture. "} },
{ ," id  :"OIG",     ," type :"Office",     ," properties" : {" name" :"Office of Inspector General",     ," description" :"Provides independent oversight through audits & investigations of USDA programs"}}
],

"edges":[
{"source" :"USDA",       ,"target" :"Farm_Production_Conservation",       ,"type" :"has_mission_area"},
{"source" :"USDA",       ,"target" :"Food_Nutrition_Consumer_Services",       ,"type" :"has_mission_area"},
{"source" :"USDA",       ,"target" :"Food_Safety",       ,"type" :"has_mission_area"},
{"source" :"USDA",       ,"target" :"Marketing_Regulatory_Programs",       ,"type" :"has_mission_area"},
{"source" :"USDA",       ,"target" :"Natural_Resources_Environment",       ,"type" :"has_mission_area"},
{"source" :"USDA",       ,"target" :"Research_Education_Economics",       ,"type" :"has_mission_area"},
{"source" :"USDA",       ,"target" :"Rural_Development",       ,"type" :"has_mission_area"},
{"source" :"USDA",       ,"target" :"Trade_Foreign_Affairs",       ,"type" :"has_mission_area"}
]
}'''

# Fix the JSON by cleaning it up
def fix_json(json_str):
    # Remove trailing commas and fix formatting issues
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix extra commas in objects
    json_str = re.sub(r'{([^}]+),\s*}', r'{\1}', json_str)
    
    # Remove spaces around keys and fix quotes
    json_str = re.sub(r'(\s+)"(.*?)"(\s*):', r'"\\2":', json_str)
    
    return json_str

# Fix the JSON data
fixed_json = fix_json(json_data)

try:
    parsed_data = json.loads(fixed_json)
    print("JSON parsing successful!")
    print(f"Number of nodes: {len(parsed_data['nodes'])}")
    print(f"Number of edges: {len(parsed_data['edges'])}")
except Exception as e:
    print(f"Error in JSON parsing: {e}")

# Now create the Graphviz visualization
from graphviz import Graph

def create_graphviz_from_json(data):
    dot = Graph(comment='USDA Organization', format='png')
    
    # Add nodes with labels based on their type and properties
    for node in data['nodes']:
        node_id = node['id']
        node_type = node['type']
        name = node['properties']['name']
        
        if node_type == 'Department':
            dot.node(node_id, f"{name}\n({node_type})", shape='box', style='filled', fillcolor='lightblue')
        elif node_type == 'MissionArea':
            dot.node(node_id, f"{name}\n({node_type})", shape='ellipse', style='filled', fillcolor='lightyellow')
        else:  # Agency or Office
            description = node['properties'].get('description', '')
            if description:
                label = f"{name}\n{description[:50]}..."
            else:
                label = name
            dot.node(node_id, f"{label}\n({node_type})", shape='box', style='filled', fillcolor='lightgreen')
    
    # Add edges between nodes
    for edge in data['edges']:
        source = edge['source']
        target = edge['target']
        edge_type = edge.get('type', 'related')
        
        dot.edge(source, target, label=edge_type)
    
    return dot

# Create and render the graph
try:
    graph = create_graphviz_from_json(parsed_data)
    graph.render(filename='usda_organization', directory='./images', cleanup=True)
    print("Graph created successfully!")
except Exception as e:
    print(f"Error creating graph: {e}")