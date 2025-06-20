from collections import defaultdict

def afn_to_epsilon_afn(states, transitions):
    # Conversion simple : ajoute epsilon-transitions vides
    new_transitions = {}
    for state in states:
        str_state = str(state)
        new_transitions[str_state] = transitions.get(str_state, {})
        if "ε" not in new_transitions[str_state]:
            new_transitions[str_state]["ε"] = []
    return new_transitions


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
