def afd_to_afdc(states, alphabet, transitions):
    states = [str(s) for s in states]
    alphabet = list(alphabet)
    transitions = {str(k): {a: str(v) for a, v in vdict.items()} for k, vdict in transitions.items()}

    sink = "P"  # état puits
    all_states = set(states)
    completed_transitions = {}

    for state in all_states:
        completed_transitions[state] = {}
        for symbol in alphabet:
            if symbol in transitions.get(state, {}):
                completed_transitions[state][symbol] = transitions[state][symbol]
            else:
                completed_transitions[state][symbol] = sink

    # Ajout de l’état puits avec boucles sur tous les symboles
    completed_transitions[sink] = {symbol: sink for symbol in alphabet}
    all_states.add(sink)

    return {
        "states": list(all_states),
        "alphabet": alphabet,
        "transitions": completed_transitions,
        "sink_state": sink
    }
