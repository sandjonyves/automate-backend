def minimize_moore(states, alphabet, initial_state, final_states, transitions):
    states = [str(s) for s in states]
    alphabet = [a for a in alphabet if a != "ε"]
    final_states = set(map(str, final_states))
    non_final_states = set(states) - final_states

    # Initial partition : finals vs non-finals
    partitions = [final_states, non_final_states]
    stable = False

    def find_block(state, parts):
        for i, p in enumerate(parts):
            if state in p:
                return i
        return None

    while not stable:
        new_partitions = []
        stable = True

        for group in partitions:
            blocks = {}
            for state in group:
                signature = []
                for symbol in alphabet:
                    dest = transitions.get(state, {}).get(symbol)
                    if dest is not None:
                        dest = str(dest)
                        sig = find_block(dest, partitions)
                    else:
                        sig = None
                    signature.append(sig)
                signature = tuple(signature)
                blocks.setdefault(signature, set()).add(state)

            new_blocks = list(blocks.values())
            new_partitions.extend(new_blocks)
            if len(new_blocks) > 1:
                stable = False

        partitions = new_partitions

    # Renommer les nouveaux états
    state_names = {frozenset(p): f"S{i}" for i, p in enumerate(partitions)}
    state_map = {}
    for p in partitions:
        name = state_names[frozenset(p)]
        for s in p:
            state_map[s] = name

    new_states = list(state_names.values())
    new_initial = state_map[str(initial_state)]
    new_finals = list({state_map[s] for s in final_states})
    new_transitions = {}

    for group in partitions:
        rep = next(iter(group))
        new_src = state_map[rep]
        new_transitions[new_src] = {}
        for symbol in alphabet:
            dest = transitions.get(rep, {}).get(symbol)
            if dest is not None:
                if isinstance(dest, list):
                    # Plusieurs cibles -> groupe d'états -> clé canonique
                    dest_key = tuple(sorted(state_map[d] for d in dest))
                    # Comme on veut un automate déterministe minimal, la cible est un seul état (groupe),
                    # donc on peut prendre n'importe quel dans dest_key (ils sont égaux en minimisation)
                    # Ici on prend le premier
                    new_transitions[new_src][symbol] = dest_key[0]
                else:
                    new_transitions[new_src][symbol] = state_map[str(dest)]
    return {
        "states": new_states,
        "alphabet": alphabet,
        "initial_state": new_initial,
        "final_states": new_finals,
        "transitions": new_transitions
    }
