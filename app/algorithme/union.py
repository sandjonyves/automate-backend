from typing import Set, Dict, List

class Automate:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[str, Dict[str, List[str]]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # Clés : états, valeurs : {symbole: [états suivants]}
        self.initial_state = initial_state
        self.final_states = final_states

def union_automates(automate1: Automate, automate2: Automate) -> Automate:
    """Calcule l'union de deux automates."""
    combined_alphabet = automate1.alphabet.union(automate2.alphabet)
    new_initial_state = "q_start"

    # Renommage des états pour éviter les conflits
    states1 = {f"a1_{state}" for state in automate1.states}
    states2 = {f"a2_{state}" for state in automate2.states}
    new_states = states1.union(states2).union({new_initial_state})

    # Initialisation des nouvelles transitions
    new_transitions: Dict[str, Dict[str, List[str]]] = {}

    # Ajout des transitions renommées de automate1
    for state, trans_dict in automate1.transitions.items():
        renamed_state = f"a1_{state}"
        new_transitions[renamed_state] = {}
        for symbol, destinations in trans_dict.items():
            if not isinstance(destinations, list):
                destinations = [destinations]
            new_transitions[renamed_state][symbol] = [f"a1_{dst}" for dst in destinations]

    # Ajout des transitions renommées de automate2
    for state, trans_dict in automate2.transitions.items():
        renamed_state = f"a2_{state}"
        new_transitions[renamed_state] = {}
        for symbol, destinations in trans_dict.items():
            if not isinstance(destinations, list):
                destinations = [destinations]
            new_transitions[renamed_state][symbol] = [f"a2_{dst}" for dst in destinations]

    # Ajout des transitions depuis le nouvel état initial
    new_transitions[new_initial_state] = {}
    # On ajoute une transition ε vers les deux automates
    new_transitions[new_initial_state][""] = [
        f"a1_{automate1.initial_state}",
        f"a2_{automate2.initial_state}"
    ]

    # Détermination des nouveaux états finaux
    new_final_states = {
        f"a1_{state}" for state in automate1.final_states
    }.union({
        f"a2_{state}" for state in automate2.final_states
    })

    return Automate(
        states=new_states,
        alphabet=combined_alphabet,
        transitions=new_transitions,
        initial_state=new_initial_state,
        final_states=new_final_states
    )
