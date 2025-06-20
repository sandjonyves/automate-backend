from app.algorithme.afn_to_afd import afn_to_afd
from app.algorithme.afd_to_afdc import afd_to_afdc
from app.algorithme.minimisation_moore import minimize_moore

def canonize_automate(states, alphabet, initial_state, final_states, transitions, is_deterministic):
    # Étape 1 : déterminisation si nécessaire
    if not is_deterministic:
        afd = afn_to_afd(states, alphabet, initial_state, final_states, transitions)
    else:
        afd = {
            "states": states,
            "alphabet": alphabet,
            "initial_state": initial_state,
            "final_states": final_states,
            "transitions": transitions
        }

    # Étape 2 : complétion de l’AFD
    afd_complet = afd_to_afdc(
        states=afd["states"],
        alphabet=afd["alphabet"],
        transitions=afd["transitions"]
    )

    # Étape 3 : minimisation
    afd_min = minimize_moore(
        states=afd_complet["states"],
        alphabet=afd["alphabet"],
        initial_state=afd["initial_state"],
        final_states=afd["final_states"],
        transitions=afd_complet["transitions"]
    )

    return afd_min
