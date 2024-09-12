def normalize_relation_score(matrix_relation, n_communities):
  # normalizzazione tra -1 e +1
  for first_comm in range(n_communities):
    maximum = max(matrix_relation[first_comm])
    minimum = abs(min(matrix_relation[first_comm]))
    for second_comm in range(n_communities):
      if matrix_relation[first_comm][second_comm] >= 0 and maximum != 0:
        matrix_relation[first_comm][second_comm] /= maximum
      elif minimum != 0:
        matrix_relation[first_comm][second_comm] /= minimum
  return matrix_relation

def compute_direct_relation(attacks_graph,
                            messages_graph,
                            trades_graph,
                            n_communities,
                            norms = False):
  matrix_relation = [[0.0 for _ in range(n_communities)] for _ in range(n_communities)]

  for e in attacks_graph.es:
      if e.target != e.source:
        source = int(attacks_graph.vs[e.source]['label'])
        target = int(attacks_graph.vs[e.target]['label'])
        matrix_relation[source][target] = matrix_relation[source][target] - 0.1 * e['n_interactions']
        matrix_relation[target][source] = matrix_relation[target][source] - 0.1 * e['n_interactions']

  for e in trades_graph.es:
    if e.target != e.source:
      source = int(trades_graph.vs[e.source]['label'])
      target = int(trades_graph.vs[e.target]['label'])
      matrix_relation[source][target] = matrix_relation[source][target] + 0.1 * e['n_interactions']
      matrix_relation[target][source] = matrix_relation[target][source] + 0.1 * e['n_interactions']

  if norms == True:
    matrix_relation = normalize_relation_score(matrix_relation, n_communities)
  return matrix_relation

def compute_indirect_relation(attacks_graph,
                              messages_graph,
                              n_communities,
                              threshold = 10,
                              threshold_jaccard = 0.5,
                              norms = False,
                              const = False):
  matrix_relation = [[0.0 for _ in range(n_communities)] for _ in range(n_communities)]

  for e in messages_graph.es:
    if e.target != e.source:
      source_label = messages_graph.vs[e.source]['label']
      target_label = messages_graph.vs[e.target]['label']

      first_attacks = attacks_graph.es.select(_source_eq = attacks_graph.vs.select(label_eq = source_label)[0])
      second_attacks = attacks_graph.es.select(_source_eq = attacks_graph.vs.select(label_eq = target_label)[0])

      first_attacks_filtered = set()
      second_attacks_filtered = set()

      for first, second in zip(first_attacks, second_attacks):
        if first['n_interactions'] >= threshold:
          first_attacks_filtered.add(first.target)
        if second['n_interactions'] >= threshold:
          second_attacks_filtered.add(second.target)

      if len(first_attacks_filtered) !=  0 or len(second_attacks_filtered) != 0:
        jaccard_index = len(set.intersection(first_attacks_filtered, second_attacks_filtered)) / len(set.union(first_attacks_filtered, second_attacks_filtered))

        if jaccard_index > threshold_jaccard:
          aggiunta = 0
          if const == True:
            aggiunta = 0.1
          else:
            aggiunta = 0.5 * e['n_interactions']
          matrix_relation[int(source_label)][int(target_label)] = matrix_relation[int(source_label)][int(target_label)] + aggiunta
          matrix_relation[int(target_label)][int(source_label)] = matrix_relation[int(target_label)][int(source_label)] + aggiunta

  if norms == True:
    matrix_relation = normalize_relation_score(matrix_relation, n_communities)
  return matrix_relation

def sum_matrix(m1, m2, m3, n_communities, weight = [1, 1, 1]):
  ris = [[0 for _ in range(n_communities)] for _ in range(n_communities)]
  for i in range(n_communities):
    for j in range(n_communities):
      if m1 != None:
        ris[i][j] += weight[0] * m1[i][j]
      if m2 != None:
        ris[i][j] += weight[1] * m2[i][j]
      if m3 != None:
        ris[i][j] += weight[2] * m3[i][j]

  return ris

def relation_score(attacks_graphs,
                   messages_graphs,
                   trades_graphs,
                   n_communities,
                   weight = [1, 1, 1],
                   norms = False,
                   const = False):
  ris = []

  direct = compute_direct_relation(attacks_graphs[0], messages_graphs[0], trades_graphs[0], n_communities, norms = norms)
  indirect = compute_indirect_relation(attacks_graphs[0], messages_graphs[0], n_communities, norms = norms, const = const)

  if norms == True:
   direct = normalize_relation_score(direct, n_communities)

  m = sum_matrix(None, direct, indirect, n_communities, weight)

  if norms == True:
   m = normalize_relation_score(m, n_communities)

  ris.append(m)

  for day in range(1, len(attacks_graphs)):
    direct = compute_direct_relation(attacks_graphs[day], messages_graphs[day], trades_graphs[day], n_communities, norms = norms)
    indirect = compute_indirect_relation(attacks_graphs[day], messages_graphs[day], n_communities, norms = norms, const = const)

    if norms == True:
      direct = normalize_relation_score(direct, n_communities)

    m = sum_matrix(ris[-1], direct, indirect, n_communities, weight)

    if norms == True:
      m = normalize_relation_score(m, n_communities)

    ris.append(m)

  if norms == False:
    for day in range(len(ris)):
      ris[day] = normalize_relation_score(ris[day], n_communities)
  return ris