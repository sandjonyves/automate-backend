from typing import Set, Dict, Tuple

class Automate:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[Tuple[str, str], Set[str]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # Clés : (état, symbole), valeurs : ensemble d'états suivants
        self.initial_state = initial_state
        self.final_states = final_states

def concatenate_automates(automate1: Automate, automate2: Automate) -> Automate:
    """Calcule la concaténation de deux automates en reliant les états finaux de A1 à l'état initial de A2."""
    # Vérifier la compatibilité des alphabets
    if not automate1.alphabet.issubset(automate2.alphabet) or not automate2.alphabet.issubset(automate1.alphabet):
        raise ValueError("Alphabets must be compatible for concatenation")

    # Nouveaux états : union des états de A1 et A2
    new_states = automate1.states.union(automate2.states)
    
    # Nouvel alphabet : intersection des alphabets
    new_alphabet = automate1.alphabet.intersection(automate2.alphabet)
    
    # Nouvelles transitions : combinaison des transitions de A1 et A2
    new_transitions = automate1.transitions.copy()
    new_transitions.update(automate2.transitions)
    
    # Ajouter des transitions ε des états finaux de A1 vers l'état initial de A2
    epsilon_symbol = "ε"  # Symbole fictif pour la transition
    for final_state in automate1.final_states:
        new_transitions[(final_state, epsilon_symbol)] = {automate2.initial_state}
        print(f"Added ε-transition: {final_state} --ε--> {automate2.initial_state}")
    
    # Nouvel état initial : celui de A1
    new_initial_state = automate1.initial_state
    
    # Nouveaux états finaux : ceux de A2
    new_final_states = automate2.final_states
    
    return Automate(
        states=new_states,
        alphabet=new_alphabet,
        transitions=new_transitions,
        initial_state=new_initial_state,
        final_states=new_final_states
    )