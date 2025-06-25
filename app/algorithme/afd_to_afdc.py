def afd_to_afdc(states, alphabet, transitions):
    """
    Complète un AFD en ajoutant un état puits, en format AFN-compatible (destinations = listes).
    """
    states = [str(s) for s in states]
    alphabet = list(alphabet)
    sink = "P"
    completed_transitions = {}

    for state in states:
        completed_transitions[state] = {}
        for symbol in alphabet:
            if symbol in transitions.get(state, {}):
                dest = transitions[state][symbol]
                # force la destination à être une liste
                if isinstance(dest, list):
                    completed_transitions[state][symbol] = [str(d) for d in dest]
                else:
                    completed_transitions[state][symbol] = [str(dest)]
            else:
                completed_transitions[state][symbol] = [sink]

    completed_transitions[sink] = {symbol: [sink] for symbol in alphabet}
    all_states = set(states)
    all_states.add(sink)

    return {
        "states": list(all_states),
        "alphabet": alphabet,
        "transitions": completed_transitions,
        "sink_state": sink
    }
