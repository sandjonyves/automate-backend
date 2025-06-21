import random

def afd_to_epsilon_afn(states, alphabet, transitions):
    new_transitions = {}
    
    # D'abord copier toutes les transitions existantes
    for state in states:
        str_state = str(state)
        new_transitions[str_state] = transitions.get(str_state, {}).copy()
        if "ε" not in new_transitions[str_state]:
            new_transitions[str_state]["ε"] = []
    
    # Ajouter des transitions epsilon aléatoires
    for state in states:
        str_state = str(state)
        # Nombre aléatoire de transitions epsilon à ajouter (0 à 3 par exemple)
        num_epsilon = random.randint(0, 3)
        
        for _ in range(num_epsilon):
            # Choisir un état destination aléatoire
            dest_state = random.choice(states)
            # Ajouter la transition epsilon si elle n'existe pas déjà
            if dest_state not in new_transitions[str_state]["ε"]:
                new_transitions[str_state]["ε"].append(dest_state)

    return new_transitions
