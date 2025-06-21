from typing import Set, Dict, Tuple

class Automate:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[str, Dict[str, str]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # Clés : états, valeurs : {symbole: état suivant}
        self.initial_state = initial_state
        self.final_states = final_states

def union_automates(automate1: Automate, automate2: Automate) -> Automate:
    """Calcule l'union de deux automates en créant un nouvel automate."""
    # Vérifier que les alphabets sont compatibles
    combined_alphabet = automate1.alphabet.union(automate2.alphabet)
    
    # Créer un nouvel état initial
    new_initial_state = "q_start"
    
    # Combiner les états (ajouter un préfixe pour éviter les collisions)
    states1 = {f"a1_{state}" for state in automate1.states}
    states2 = {f"a2_{state}" for state in automate2.states}
    new_states = states1.union(states2).union({new_initial_state})
    
    # Combiner les transitions
    new_transitions = {}
    # Transitions depuis le nouvel état initial
    new_transitions[f"q_start_"] = {f"a1_{automate1.initial_state}", f"a2_{automate2.initial_state}"}
    
    # Ajouter les transitions des deux automates avec préfixe
    for state, trans_dict in automate1.transitions.items():
        for symbol, next_state in trans_dict.items():
            new_transitions[f"a1_{state}_{symbol}"] = {f"a1_{next_state}"}
            print(f"Processing automate1: state={state}, symbol={symbol}, next_state={next_state}")
    
    for state, trans_dict in automate2.transitions.items():
        for symbol, next_state in trans_dict.items():
            new_transitions[f"a2_{state}_{symbol}"] = {f"a2_{next_state}"}
            print(f"Processing automate2: state={state}, symbol={symbol}, next_state={next_state}")
    
    # Combiner les états finaux
    new_final_states = {f"a1_{state}" for state in automate1.final_states}.union(
        {f"a2_{state}" for state in automate2.final_states}
    )
    print(f"New final states: {new_final_states}")
    
    return Automate(
        states=new_states,
        alphabet=combined_alphabet,
        transitions=new_transitions,
        initial_state=new_initial_state,
        final_states=new_final_states
    )