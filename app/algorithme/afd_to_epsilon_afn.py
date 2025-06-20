def afd_to_epsilon_afn(states, alphabet, transitions):
    new_transitions = {}

    for state in states:
        state = str(state)
        new_transitions[state] = {}
        for symbol in alphabet:
            dest = transitions.get(state, {}).get(symbol)
            if dest is not None:
                new_transitions[state][symbol] = [str(dest)]
        # Ajoute une transition ε vide (optionnelle mais utile)
        new_transitions[state]["ε"] = []

    return new_transitions
