from collections import defaultdict

def afn_to_epsilon_afn(states, initial_states, transitions):
    """
    Convertit un AFN en AFN-ε en ajoutant un nouvel état avec une transition ε vers les anciens états initiaux.
    
    :param states: Liste des états (ex. ["q0", "q1"])
    :param initial_states: Liste des anciens états initiaux (ex. ["q0"])
    :param transitions: Dictionnaire des transitions (ex. {"q0": {"a": ["q1"]}})
    :return: Dictionnaire contenant les nouveaux états, transitions, et nouvel état initial
    """

    states = [str(s) for s in states]
    initial_states = [str(s) for s in initial_states]
    transitions = {str(k): {a: list(map(str, v)) for a, v in sym.items()} for k, sym in transitions.items()}

    new_initial_state = "S"
    new_states = [new_initial_state] + states

    new_transitions = {}
    new_transitions[new_initial_state] = transitions.get(new_initial_state, {})
    if "ε" not in new_transitions[new_initial_state]:
            new_transitions[new_initial_state]["ε"] = []
    # Copier les anciennes transitions
    # for state in new_states:
    #     new_transitions[state] = transitions.get(state, {})
    #     if "ε" not in new_transitions[state]:
    #         new_transitions[state]["ε"] = []

    # Ajouter epsilon transition depuis le nouvel état vers les anciens initiaux
    new_transitions[new_initial_state]["ε"] = initial_states

    return {
        "states": new_states,
        "initial_state": new_initial_state,
        "transitions": new_transitions
    }

def epsilon_closure(state, transitions):
    """Retourne l’ensemble des états atteignables depuis `state` via ε-transitions"""
    closure = set([state])
    stack = [state]
    while stack:
        current = stack.pop()
        for next_state in transitions.get(current, {}).get("ε", []):
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure


def epsilon_afn_to_afn(states, alphabet, transitions):
    alphabet = [a for a in alphabet if a != "ε"]
    new_transitions = defaultdict(lambda: defaultdict(set))

    for state in states:
        closure = epsilon_closure(state, transitions)
        for symbol in alphabet:
            target_states = set()
            for cstate in closure:
                for dest in transitions.get(cstate, {}).get(symbol, []):
                    target_states |= epsilon_closure(dest, transitions)
            if target_states:
                new_transitions[state][symbol] |= target_states

    # Convert sets to lists
    final_transitions = {}
    for src in new_transitions:
        final_transitions[src] = {}
        for sym in new_transitions[src]:
            final_transitions[src][sym] = list(new_transitions[src][sym])
    return final_transitions
