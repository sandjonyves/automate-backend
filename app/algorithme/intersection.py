from typing import Set, Dict, Tuple

class Automate:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[Tuple[str, str], Set[str]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # Clés : (état, symbole), valeurs : ensemble d'états suivants
        self.initial_state = initial_state
        self.final_states = final_states

def intersect_automates(automate1: Automate, automate2: Automate) -> Automate:
    """Calcule l'intersection de deux automates en utilisant le produit cartésien."""
    if not automate1.alphabet.issubset(automate2.alphabet) or not automate2.alphabet.issubset(automate1.alphabet):
        raise ValueError("Alphabets must be compatible for intersection")

    new_initial_state = f"{automate1.initial_state}_{automate2.initial_state}"
    new_states = {f"{s1}_{s2}" for s1 in automate1.states for s2 in automate2.states}
    new_transitions = {}
    for s1 in automate1.states:
        for s2 in automate2.states:
            current_state = f"{s1}_{s2}"
            for symbol in automate1.alphabet:
                next_s1_set = automate1.transitions.get((s1, symbol), set())
                next_s2_set = automate2.transitions.get((s2, symbol), set())
                if next_s1_set and next_s2_set:
                    next_s1 = next(iter(next_s1_set))
                    next_s2 = next(iter(next_s2_set))
                    if next_s1 and next_s2:  # Vérification supplémentaire
                        next_state = f"{next_s1}_{next_s2}"
                        new_transitions[(current_state, symbol)] = {next_state}
                        print(f"Processing: state={current_state}, symbol={symbol}, next_state={next_state}")
                    else:
                        print(f"Warning: Invalid next state for {current_state} with symbol {symbol}")

    new_final_states = {f"{s1}_{s2}" for s1 in automate1.final_states for s2 in automate2.final_states}
    print(f"New final states: {new_final_states}")

    return Automate(
        states=new_states,
        alphabet=automate1.alphabet,
        transitions=new_transitions,
        initial_state=new_initial_state,
        final_states=new_final_states
    )