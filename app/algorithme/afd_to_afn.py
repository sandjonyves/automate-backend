def afd_to_afn(states, alphabet, transitions, initial_state, final_states,
                          entry_state="qi", exit_state="qif"):
    """
    Ajoute deux états :
    - ENTRY : accessible depuis l'état initial via le premier symbole de l'alphabet
    - EXIT : accessible depuis tous les états finaux via le même symbole

    Ne modifie pas l'alphabet.

    Returns:
        Un automate mis à jour avec ENTRY et EXIT.
    """
    if not alphabet:
        raise ValueError("L'alphabet ne peut pas être vide.")
    
    # Nettoyage & conversions
    states = [str(s) for s in states]
    alphabet = list(alphabet)
    transitions = {str(state): {symb: [dst] if not isinstance(dst, list) else dst for symb, dst in trans.items()}
                   for state, trans in transitions.items()}
    initial_state = str(initial_state)
    final_states = [str(f) for f in final_states]

    # Choisir le premier symbole de l'alphabet
    symbol = alphabet[0]

    # Ajouter ENTRY
    if entry_state in states or exit_state in states:
        raise ValueError("Les noms ENTRY ou EXIT existent déjà dans les états.")
    states.extend([entry_state, exit_state])

    # Ajout de ENTRY
    transitions.setdefault(initial_state, {})
    transitions[initial_state].setdefault(symbol, []).append(entry_state)
    transitions[entry_state] = {}  # pas de transition sortante pour ENTRY (par défaut)

    # Ajout de EXIT
    for f in final_states:
        transitions.setdefault(f, {})
        transitions[f].setdefault(symbol, []).append(exit_state)
    transitions[exit_state] = {}  # pas de transition sortante

    return {
        "states": states,
        "alphabet": alphabet,
        "transitions": transitions,
        "initial_state": initial_state,
        "final_states": final_states
    }
