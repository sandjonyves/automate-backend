from collections import deque, defaultdict

def find_accessibles(states, initial_state, transitions):
    visited = set()
    queue = deque([initial_state])
    while queue:
        state = queue.popleft()
        if state not in visited:
            visited.add(state)
            for symbol in transitions.get(state, {}):
                for next_state in transitions[state][symbol]:
                    if next_state not in visited:
                        queue.append(next_state)
    return visited

def find_co_accessibles(states, final_states, transitions):
    # Construire le graphe inversé
    reversed_graph = defaultdict(set)
    for src in transitions:
        for symbol in transitions[src]:
            for dest in transitions[src][symbol]:
                reversed_graph[dest].add(src)

    visited = set()
    queue = deque(final_states)
    while queue:
        state = queue.popleft()
        if state not in visited:
            visited.add(state)
            for pred in reversed_graph[state]:
                if pred not in visited:
                    queue.append(pred)
    return visited

def identify_states(states, initial_state, final_states, transitions):
    states = [str(s) for s in states]
    initial_state = str(initial_state)
    final_states = [str(f) for f in final_states]

    # Normalize transitions: ensure all destinations are lists of strings
    norm_trans = {}
    for src, sym_dict in transitions.items():
        src = str(src)
        norm_trans[src] = {}
        for sym, dests in sym_dict.items():
            if isinstance(dests, str):
                norm_trans[src][sym] = [str(dests)]
            else:
                norm_trans[src][sym] = [str(d) for d in dests]

    accessibles = find_accessibles(states, initial_state, norm_trans)
    co_accessibles = find_co_accessibles(states, final_states, norm_trans)
    utiles = accessibles.intersection(co_accessibles)

    return {
        "accessibles": sorted(accessibles),
        "co_accessibles": sorted(co_accessibles),
        "utiles": sorted(utiles)
    }
