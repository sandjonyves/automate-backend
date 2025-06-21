from typing import Set, Dict, Tuple
from collections import defaultdict
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# ---------- CLASSE AUTOMATE ----------

class Automate:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[Tuple[str, str], Set[str]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions  # Clés : (état, symbole), valeurs : ensemble d'états suivants
        self.initial_state = initial_state
        self.final_states = final_states

# ---------- CONCATENATION ----------

def concatenate_automates(automate1: Automate, automate2: Automate) -> Automate:
    if automate1.alphabet != automate2.alphabet:
        raise ValueError("Alphabets must be identical for concatenation")

    new_states = automate1.states.union(automate2.states)
    new_alphabet = automate1.alphabet

    new_transitions = automate1.transitions.copy()
    new_transitions.update(automate2.transitions)

    # Ajout des ε-transitions
    epsilon_symbol = "ε"
    for final_state in automate1.final_states:
        new_transitions[(final_state, epsilon_symbol)] = {automate2.initial_state}

    new_initial_state = automate1.initial_state
    new_final_states = automate2.final_states

    return Automate(
        states=new_states,
        alphabet=new_alphabet,
        transitions=new_transitions,
        initial_state=new_initial_state,
        final_states=new_final_states
    )
