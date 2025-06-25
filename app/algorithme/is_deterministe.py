def is_deterministic_automaton(states, alphabet, transitions, initial_state, final_states):
    """
    Vérifie si un automate est déterministe (DFA).

    Args:
        states (list): liste des états
        alphabet (list): liste des symboles (ex: ['a', 'b'])
        transitions (dict): transitions, ex: {'q0': {'a': 'q1'}}
        initial_state (str): l’état initial
        final_states (list): liste des états finaux

    Returns:
        bool: True si l'automate est déterministe, False sinon
    """
    if initial_state not in states:
        return False

    for state, trans in transitions.items():
        if state not in states:
            return False
        for symbol, dest in trans.items():
            if symbol == 'ε':
                return False  # interdit en DFA
            if symbol not in alphabet:
                return False
            if isinstance(dest, list):
                # si plusieurs destinations => non-déterministe
                if len(dest) != 1:
                    return False
            elif isinstance(dest, str):
                pass  # OK
            else:
                return False  # mauvais format

    return True
