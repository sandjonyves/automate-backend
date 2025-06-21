from typing import Set, Dict, Tuple
from collections import defaultdict
from queue import Queue

class CanonicalAutomate:  # Renommé pour éviter la confusion avec le modèle
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[Tuple[str, str], Set[str]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

def determinize(automate: CanonicalAutomate) -> CanonicalAutomate:
    """Transforme un AFN en AFD en utilisant l'algorithme des sous-ensembles."""
    new_states = set()
    new_transitions = {}
    new_final_states = set()
    
    state_queue = Queue()
    initial_state_set = frozenset([automate.initial_state])
    state_queue.put(initial_state_set)
    new_states.add(initial_state_set)
    
    while not state_queue.empty():
        current_state = state_queue.get()
        for symbol in automate.alphabet:
            next_states = set()
            for state in current_state:
                next_states.update(automate.transitions.get((state, symbol), set()))
            next_state = frozenset(next_states)
            if next_state:
                new_transitions[(current_state, symbol)] = next_state
                if next_state not in new_states:
                    new_states.add(next_state)
                    state_queue.put(next_state)
                if any(state in automate.final_states for state in next_state):
                    new_final_states.add(next_state)
    
    state_map = {state: f"q{index}" for index, state in enumerate(new_states)}
    final_transitions = {}
    for (from_state, symbol), to_state in new_transitions.items():
        final_transitions[(state_map[from_state], symbol)] = {state_map[to_state]}
    
    return CanonicalAutomate(
        states={state_map[state] for state in new_states},
        alphabet=automate.alphabet,
        transitions=final_transitions,
        initial_state=state_map[initial_state_set],
        final_states={state_map[state] for state in new_final_states}
    )

def complete(automate: CanonicalAutomate) -> CanonicalAutomate:
    """Rend l'automate complet en ajoutant un état poubelle si nécessaire."""
    is_complete = True
    for state in automate.states:
        for symbol in automate.alphabet:
            if (state, symbol) not in automate.transitions:
                is_complete = False
                break
        if not is_complete:
            break
    
    if is_complete:
        return automate
    
    new_states = automate.states | {"puits"}
    new_transitions = automate.transitions.copy()
    
    for state in new_states:
        for symbol in automate.alphabet:
            if (state, symbol) not in new_transitions:
                new_transitions[(state, symbol)] = {"puits"}
    
    return CanonicalAutomate(
        states=new_states,
        alphabet=automate.alphabet,
        transitions=new_transitions,
        initial_state=automate.initial_state,
        final_states=automate.final_states
    )

def minimize(automate: CanonicalAutomate) -> CanonicalAutomate:
    """Minimise l'automate en utilisant l'algorithme de partition."""
    P = [automate.final_states, automate.states - automate.final_states]
    P = [p for p in P if p]
    W = [automate.final_states]
    
    while W:
        A = W.pop()
        for symbol in automate.alphabet:
            X = set()
            for state in automate.states:
                next_states = automate.transitions.get((state, symbol), set())
                if next_states & A:
                    X.add(state)
            new_P = []
            new_W = []
            for Y in P:
                Y1 = Y & X
                Y2 = Y - X
                if Y1 and Y2:
                    new_P.append(Y1)
                    new_P.append(Y2)
                    new_W.append(Y1 if len(Y1) <= len(Y2) else Y2)
                else:
                    new_P.append(Y)
            P = new_P
            W.extend(new_W)
    
    state_map = {state: f"q{index}" for index, partition in enumerate(P) for state in partition}
    new_states = {f"q{index}" for index in range(len(P))}
    new_transitions = {}
    new_final_states = set()
    
    for partition, new_state in zip(P, new_states):
        rep_state = next(iter(partition))
        if rep_state in automate.final_states:
            new_final_states.add(new_state)
        for symbol in automate.alphabet:
            next_states = automate.transitions.get((rep_state, symbol), set())
            if next_states:
                for next_partition, next_new_state in zip(P, new_states):
                    if next_states & next_partition:
                        new_transitions[(new_state, symbol)] = {next_new_state}
                        break
    
    new_initial_state = state_map[automate.initial_state]
    
    return CanonicalAutomate(
        states=new_states,
        alphabet=automate.alphabet,
        transitions=new_transitions,
        initial_state=new_initial_state,
        final_states=new_final_states
    )

def canonize(automate: CanonicalAutomate) -> CanonicalAutomate:
    """Canonise l'automate : déterminisation, complétion, minimisation."""
    det_automate = determinize(automate)
    complete_automate = complete(det_automate)
    minimized_automate = minimize(complete_automate)
    return minimized_automate