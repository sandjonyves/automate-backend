def afn_to_afd(alphabet, states, initial_state, final_states, transitions):
    from collections import deque

    def state_set_name(state_set):
        return '{' + ','.join(sorted(state_set)) + '}'

    afd_states = set()
    afd_transitions = {}
    afd_final_states = set()

    start = frozenset([initial_state])
    queue = deque([start])
    visited = set([start])

    while queue:
        current = queue.popleft()
        current_name = state_set_name(current)
        afd_states.add(current_name)
        afd_transitions[current_name] = {}

        for symbol in alphabet:
            next_state = set()
            for state in current:
                for dest in transitions.get(state, {}).get(symbol, []):
                    next_state.add(dest)

            if not next_state:
                continue

            next_frozen = frozenset(next_state)
            next_name = state_set_name(next_frozen)

            afd_transitions[current_name][symbol] = next_name

            if next_frozen not in visited:
                visited.add(next_frozen)
                queue.append(next_frozen)

        if current & set(final_states):
            afd_final_states.add(current_name)

    return {
        "alphabet": alphabet,
        "states": list(afd_states),
        "initial_state": state_set_name(start),
        "final_states": list(afd_final_states),
        "transitions": afd_transitions
    }
