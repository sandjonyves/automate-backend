from typing import Set, Dict, Tuple
from collections import defaultdict

class Automate:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[Tuple[str, str], Set[str]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # Clés : (état, symbole), valeurs : ensemble d'états suivants
        self.initial_state = initial_state
        self.final_states = final_states


def intersect_automates(automate1: Automate, automate2: Automate) -> Automate:
    """Calcule l'intersection de deux automates (NFA ou DFA) par produit cartésien, avec transitions multiples."""
    
    # Vérifier que les alphabets sont identiques
    if automate1.alphabet != automate2.alphabet:
        raise ValueError("Alphabets must be identical for intersection")

    new_alphabet = automate1.alphabet

    # Nouvel état initial : couple des états initiaux
    new_initial_state = f"{automate1.initial_state}_{automate2.initial_state}"

    # Construire tous les états possibles : produit cartésien des états
    new_states = set()
    for s1 in automate1.states:
        for s2 in automate2.states:
            new_states.add(f"{s1}_{s2}")

    new_transitions = defaultdict(set)  # (state, symbol) -> set(next_states)

    # Parcourir tous les nouveaux états et symboles pour créer les transitions
    for s1 in automate1.states:
        for s2 in automate2.states:
            current_state = f"{s1}_{s2}"
            for symbol in new_alphabet:
                # Obtenir l'ensemble des états cibles pour chaque automate
                next_s1_states = automate1.transitions.get((s1, symbol), set())
                next_s2_states = automate2.transitions.get((s2, symbol), set())

                # Faire le produit cartésien des états suivants
                for ns1 in next_s1_states:
                    for ns2 in next_s2_states:
                        next_state = f"{ns1}_{ns2}"
                        new_transitions[(current_state, symbol)].add(next_state)

    # États finaux : ceux où chaque composante est finale dans son automate respectif
    new_final_states = set()
    for f1 in automate1.final_states:
        for f2 in automate2.final_states:
            new_final_states.add(f"{f1}_{f2}")

    return Automate(
        states=new_states,
        alphabet=new_alphabet,
        transitions=dict(new_transitions),
        initial_state=new_initial_state,
        final_states=new_final_states
    )
