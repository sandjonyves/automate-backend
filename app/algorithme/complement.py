from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from collections import defaultdict
from typing import Set, Dict, Tuple


# Classe métier
class BaseModelAutomate:
    def __init__(self, states: Set[str], alphabet: Set[str],
                 transitions: Dict[Tuple[str, str], Set[str]],
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

# Fonction de complément
def complement_automate(automate: BaseModelAutomate) -> BaseModelAutomate:
    new_final_states = automate.states - automate.final_states
    return BaseModelAutomate(
        states=automate.states,
        alphabet=automate.alphabet,
        transitions=automate.transitions,
        initial_state=automate.initial_state,
        final_states=new_final_states
    )

# Parse les transitions depuis la base de données
def parse_transitions(transitions_dict: dict) -> Dict[Tuple[str, str], Set[str]]:
    transitions = {}
    for state, symbol_map in transitions_dict.items():
        if isinstance(symbol_map, dict):
            for symbol, targets in symbol_map.items():
                transitions[(state, symbol)] = set(targets)
    return transitions

# Prépare les transitions pour le JSON de sortie
def serialize_transitions(transitions: Dict[Tuple[str, str], Set[str]]) -> Dict[str, Dict[str, list]]:
    result = defaultdict(lambda: defaultdict(list))
    for (state, symbol), targets in transitions.items():
        result[state][symbol].extend(targets)
    return {state: dict(symbols) for state, symbols in result.items()}

# Vue DRF
