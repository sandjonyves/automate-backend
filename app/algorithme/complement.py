from typing import Set, Dict, Tuple

class Automate:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[Tuple[str, str], Set[str]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # Clés : (état, symbole), valeurs : ensemble d'états suivants
        self.initial_state = initial_state
        self.final_states = final_states

def complement_automate(automate: Automate) -> Automate:
    """Calcule le complémentaire d'un automate en transformant les états finaux en états simples
    et les états simples en états finaux."""
    # Inverser les rôles : les anciens états finaux deviennent simples, les anciens non finaux deviennent finaux
    new_final_states = automate.states - automate.final_states
    print(f"New final states (old non-final states): {new_final_states}")

    return Automate(
        states=automate.states,
        alphabet=automate.alphabet,
        transitions=automate.transitions,
        initial_state=automate.initial_state,
        final_states=new_final_states
    )