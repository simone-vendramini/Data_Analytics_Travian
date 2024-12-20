from import_graphs import *
from plot_sankey import plot_sankey_diagram
from utils import *
from manage_graphs import *

def set_community_for_player(player, community, day):
  GRAPHS_ATTACKS[day].vs.select(label = player)['community'] = community
  GRAPHS_TRADES[day].vs.select(label = player)['community'] = community
  GRAPHS_MESSAGES[day].vs.select(label = player)['community'] = community

# Load the graphs
get_graphs()
#Load the communities graphs
read_all_communities_graphs()

types_interaction = ['attack', 'trade', 'message']

for el in types_interaction:
  for day in range(len(GRAPHS_ATTACKS)):
    if el == 'attack':
      for v in COMM_GRAPHS_ATTACKS[day].vs:
        v['players'] = player_parser(v['players'])
    if el == 'trade':
      for v in COMM_GRAPHS_TRADES[day].vs:
        v['players'] = player_parser(v['players'])
    if el == 'message':
      for v in COMM_GRAPHS_MESSAGES[day].vs:
        v['players'] = player_parser(v['players'])

for day in range(len(GRAPHS_ATTACKS)):
  GRAPHS_ATTACKS[day].vs['community'] = None
for day in range(len(GRAPHS_ATTACKS)):
  GRAPHS_TRADES[day].vs['community'] = None
for day in range(len(GRAPHS_ATTACKS)):
  GRAPHS_MESSAGES[day].vs['community'] = None

for day in range(len(GRAPHS_ATTACKS)):
  for v in COMM_GRAPHS_ATTACKS[day].vs:
    for player in v['players']:
      set_community_for_player(str(player), v['label'], day)

for day in range(len(GRAPHS_ATTACKS)):
  GRAPHS_ATTACKS[day].save(NAME_FILES['attacks'] + str(day) + NAME_FILES['ext'], format="graphml")
for day in range(len(GRAPHS_ATTACKS)):
  GRAPHS_TRADES[day].save(NAME_FILES['trades'] + str(day) + NAME_FILES['ext'], format="graphml")
for day in range(len(GRAPHS_ATTACKS)):
  GRAPHS_MESSAGES[day].save(NAME_FILES['messages'] + str(day) + NAME_FILES['ext'], format="graphml")