from collections import defaultdict

import random

def afn_to_epsilon_afn(states, transitions):
    # Conversion avec ajout aléatoire de transitions epsilon
    new_transitions = {}
    
    # D'abord copier toutes les transitions existantes
    for state in states:
        str_state = str(state)
        new_transitions[str_state] = transitions.get(str_state, {}).copy()
        if "ε" not in new_transitions[str_state]:
            new_transitions[str_state]["ε"] = []
    
    # Ajouter des transitions epsilon aléatoires
    for state in states:
        str_state = str(state)
        # Nombre aléatoire de transitions epsilon à ajouter (0 à 3 par exemple)
        num_epsilon = random.randint(0, 3)
        
        for _ in range(num_epsilon):
            # Choisir un état destination aléatoire
            dest_state = random.choice(states)
            # Ajouter la transition epsilon si elle n'existe pas déjà
            if dest_state not in new_transitions[str_state]["ε"]:
                new_transitions[str_state]["ε"].append(dest_state)
    
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
