from collections import deque, defaultdict

def epsilon_closure(state, transitions):
    closure = set([state])
    stack = [state]
    while stack:
        current = stack.pop()
        for next_state in transitions.get(current, {}).get("ε", []):
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return closure

def closure_of_set(state_set, transitions):
    result = set()
    for state in state_set:
        result |= epsilon_closure(state, transitions)
    return result

def epsilon_afn_to_afd(states, alphabet, transitions, initial_state, final_states):
    states = [str(s) for s in states]
    alphabet = [a for a in alphabet if a != "ε"]
    final_states = [str(f) for f in final_states]
    initial_state = str(initial_state)

    state_map = {}
    afd_transitions = {}
    queue = deque()

    initial_closure = closure_of_set([initial_state], transitions)
    initial_key = frozenset(initial_closure)
    state_map[initial_key] = "S0"
    queue.append(initial_key)
    state_count = 1

    while queue:
        current_set = queue.popleft()
        current_name = state_map[current_set]
        afd_transitions[current_name] = {}

        for symbol in alphabet:
            next_states = set()
            for state in current_set:
                for dest in transitions.get(state, {}).get(symbol, []):
                    next_states |= closure_of_set([dest], transitions)

            if not next_states:
                continue

            next_key = frozenset(next_states)
            if next_key not in state_map:
                state_map[next_key] = f"S{state_count}"
                queue.append(next_key)
                state_count += 1

            afd_transitions[current_name][symbol] = state_map[next_key]

    afd_states = list(state_map.values())
    afd_initial_state = state_map[initial_key]
    afd_final_states = [state_map[s] for s in state_map if any(f in s for f in final_states)]

    return {
        "states": afd_states,
        "alphabet": alphabet,
        "initial_state": afd_initial_state,
        "final_states": afd_final_states,
        "transitions": afd_transitions
    }





