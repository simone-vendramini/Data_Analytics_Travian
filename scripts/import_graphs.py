import igraph as ig
from ranking import *
from typing import List, Set

NAME_FILES = {
    'attacks': './datasets/attacks-timestamped-2009-12-',
    'communities': './datasets/communities-2009-12-',
    'messages': './datasets/messages-timestamped-2009-12-',
    'trades': './datasets/trades-timestamped-2009-12-',
    'union': './datasets/union_graph_',
    'unionComm' : './datasets/union_community_graph_',
    'ext': '.graphml',
    'range_day': (1, 30)
}

NAME_FILES_COMMUNITY = {
    'path':  "./datasets/",
    'attacks': 'GRAPHS_COMM_ATTACKS_',
    'messages': 'GRAPHS_COMM_MESSAGES_',
    'trades': 'GRAPHS_COMM_TRADES_',
    'ext': '.graphml',
    'range_day': (0, 29)
}

GRAPHS_ATTACKS = [] # GRAPHS_ATTACKS[0] = grafo degli attacks al giorno 0
GRAPHS_MESSAGES = [] # GRAPHS_MESSAGES[0] = grafo dei messages al giorno 0
GRAPHS_TRADES = [] # GRAPHS_TRADES[0] = grafo dei trades al giorno 0
GT_COMMUNITIES = [] # GT_COMMUNITIES[0][1] = insieme di id di nodi che fanno parte della community 1 al giorno 0
COMM_GRAPHS_ATTACKS = []
COMM_GRAPHS_MESSAGES = [] 
COMM_GRAPHS_TRADES = []
PLAYERS_UNION_GRAPHS = []
COMM_UNION_GRAPHS = []
RELATION_MATRICES = []

def read_gt_commiunities(path : str = "communities-2009-12-1.txt") -> List[Set[int]]:
    file = open(path, "r")
    content = file.readlines()
    file.close()

    ris = []

    for community in content:
        list_of_nodes = community[:-1].split(' ')
        ris_nodes = set()
        for node in list_of_nodes:
            ris_nodes.add(int(node))
        ris.append(ris_nodes)

    return ris

def get_graphs():
    global RELATION_MATRICES
    for i in range(NAME_FILES['range_day'][0], NAME_FILES['range_day'][1] + 1):
        GRAPHS_ATTACKS.append(ig.read(NAME_FILES['attacks'] + str(i) + NAME_FILES['ext'], format="graphml"))
        GRAPHS_MESSAGES.append(ig.read(NAME_FILES['messages'] + str(i) + NAME_FILES['ext'], format="graphml"))
        GRAPHS_TRADES.append(ig.read(NAME_FILES['trades'] + str(i) + NAME_FILES['ext'], format="graphml"))
        PLAYERS_UNION_GRAPHS.append(ig.read(NAME_FILES['union'] + str(i-1) + NAME_FILES['ext'], format="graphml"))
        COMM_UNION_GRAPHS.append(ig.read(NAME_FILES['unionComm'] + str(i-1) + NAME_FILES['ext'], format="graphml"))
    read_all_communities_graphs()
    RELATION_MATRICES.clear()
    RELATION_MATRICES.extend(relation_score(COMM_GRAPHS_ATTACKS, COMM_GRAPHS_MESSAGES, COMM_GRAPHS_TRADES, 350, [0.6, 0.4, 1], norms=True, const=True))
    return GRAPHS_ATTACKS, GRAPHS_MESSAGES, GRAPHS_TRADES

def get_communities():
    for i in range(NAME_FILES['range_day'][0], NAME_FILES['range_day'][1] + 1):
        GT_COMMUNITIES.append(read_gt_commiunities(NAME_FILES['communities'] + str(i) + ".txt"))
    return GT_COMMUNITIES

def read_all_communities_graphs():
    for i in range(NAME_FILES_COMMUNITY['range_day'][0], NAME_FILES_COMMUNITY['range_day'][1] + 1):
        COMM_GRAPHS_ATTACKS.append(ig.read(NAME_FILES_COMMUNITY['path'] + NAME_FILES_COMMUNITY['attacks'] + str(i) + NAME_FILES_COMMUNITY['ext'], format="graphml"))
        COMM_GRAPHS_MESSAGES.append(ig.read(NAME_FILES_COMMUNITY['path'] + NAME_FILES_COMMUNITY['messages'] + str(i) + NAME_FILES_COMMUNITY['ext'], format="graphml"))
        COMM_GRAPHS_TRADES.append(ig.read(NAME_FILES_COMMUNITY['path'] + NAME_FILES_COMMUNITY['trades'] + str(i) + NAME_FILES_COMMUNITY['ext'], format="graphml"))

    return (COMM_GRAPHS_ATTACKS, COMM_GRAPHS_MESSAGES, COMM_GRAPHS_TRADES)