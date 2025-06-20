import string

class StateGenerator:
    def __init__(self):
        self.count = 0

    def new_state(self):
        s = f"S{self.count}"
        self.count += 1
        return s

def thompson_regex_to_epsilon_afn(regex):
    def add_concat_operator(regex):
        output = ""
        for i in range(len(regex)):
            output += regex[i]
            if i + 1 < len(regex):
                if (regex[i] not in '(|' and regex[i+1] not in '|)*'):
                    output += '.'
        return output

    def precedence(op):
        return {'*': 3, '.': 2, '|': 1}.get(op, 0)

    def to_postfix(regex):
        output = ""
        stack = []
        for char in regex:
            if char in string.ascii_letters or char.isdigit():
                output += char
            elif char == '(':
                stack.append(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    output += stack.pop()
                stack.pop()
            else:  # operator
                while stack and precedence(stack[-1]) >= precedence(char):
                    output += stack.pop()
                stack.append(char)
        while stack:
            output += stack.pop()
        return output

    def build_afn(postfix):
        gen = StateGenerator()
        stack = []

        for char in postfix:
            if char not in '*.|':
                start = gen.new_state()
                end = gen.new_state()
                transitions = {
                    start: {char: [end]},
                    end: {}
                }
                stack.append((start, end, transitions))
            elif char == '*':
                start = gen.new_state()
                end = gen.new_state()
                n_start, n_end, trans = stack.pop()
                trans.setdefault(start, {}).setdefault("ε", []).extend([n_start, end])
                trans.setdefault(n_end, {}).setdefault("ε", []).extend([n_start, end])
                trans.setdefault(end, {})
                stack.append((start, end, trans))
            elif char == '.':
                n2_start, n2_end, t2 = stack.pop()
                n1_start, n1_end, t1 = stack.pop()
                t1.setdefault(n1_end, {}).setdefault("ε", []).append(n2_start)
                merged = {**t1, **t2}
                merged.setdefault(n2_end, {})
                stack.append((n1_start, n2_end, merged))
            elif char == '|':
                start = gen.new_state()
                end = gen.new_state()
                n2_start, n2_end, t2 = stack.pop()
                n1_start, n1_end, t1 = stack.pop()
                merged = {**t1, **t2}
                merged.setdefault(start, {}).setdefault("ε", []).extend([n1_start, n2_start])
                merged.setdefault(n1_end, {}).setdefault("ε", []).append(end)
                merged.setdefault(n2_end, {}).setdefault("ε", []).append(end)
                merged.setdefault(end, {})
                stack.append((start, end, merged))

        return stack[0]

    regex = add_concat_operator(regex)
    postfix = to_postfix(regex)
    initial, final, transitions = build_afn(postfix)

    states = list(transitions.keys())
    alphabet = sorted(list(set(
        sym for trans in transitions.values() for sym in trans.keys() if sym != "ε"
    )))

    return {
        "states": states,
        "alphabet": alphabet + ["ε"],
        "initial_state": initial,
        "final_states": [final],
        "transitions": transitions
    }
