def epsilon_closure(state, transitions):
    closure = set([state])
    stack = [state]

    while stack:
        current = stack.pop()
        for next_state in transitions.get(current, {}).get("ε", []):
            if next_state not in closure:
                closure.add(next_state)
                stack.append(next_state)
    return sorted(list(closure))
