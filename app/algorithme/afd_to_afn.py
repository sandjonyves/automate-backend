def afd_to_afn(states, alphabet, transitions, initial_state, final_states):
    states = [str(s) for s in states]
    alphabet = list(alphabet)
    transitions = {str(k): {a: str(v) for a, v in vdict.items()} for k, vdict in transitions.items()}
    initial_state = str(initial_state)
    final_states = [str(f) for f in final_states]

    new_state = "N"
    new_symbol = "n"

    # Mise au format AFN : transformer toutes les transitions en liste
    afn_transitions = {}
    for state in states:
        afn_transitions[state] = {}
        for symbol, dest in transitions.get(state, {}).items():
            afn_transitions[state][symbol] = [dest]

    # Ajouter nouvel état avec transition non déterministe vers 2 états existants
    afn_transitions[new_state] = {new_symbol: states[:2]}  # prend les 2 premiers par défaut

    # Nouvelle liste d’états avec le nouveau
    new_states = [new_state] + states
    new_alphabet = list(set(alphabet + [new_symbol]))

    return {
        "states": new_states,
        "alphabet": new_alphabet,
        "transitions": afn_transitions,
        "initial_state": new_state,
        "final_states": final_states
    }
