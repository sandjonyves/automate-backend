# from collections import defaultdict
# import string

# class StateGenerator:
#     def __init__(self):
#         self.count = 0

#     def new_state(self):
#         s = f"S{self.count}"
#         self.count += 1
#         return s


# def add_concat_operator(regex):
#     output = ""
#     for i in range(len(regex)):
#         output += regex[i]
#         if i + 1 < len(regex):
#             if (
#                 regex[i] not in "(|"
#                 and regex[i + 1] not in "|)*"
#                 and not (regex[i] == '.' or regex[i + 1] == '.')
#             ):
#                 output += '.'
#     return output


# def precedence(op):
#     return {'*': 3, '.': 2, '|': 1}.get(op, 0)


# def to_postfix(regex):
#     output = ""
#     stack = []
#     for char in regex:
#         if char in string.ascii_letters or char.isdigit():
#             output += char
#         elif char == '(':
#             stack.append(char)
#         elif char == ')':
#             while stack and stack[-1] != '(':
#                 output += stack.pop()
#             if not stack:
#                 raise ValueError("Unmatched parentheses")
#             stack.pop()
#         else:
#             while stack and precedence(stack[-1]) >= precedence(char):
#                 output += stack.pop()
#             stack.append(char)
#     while stack:
#         if stack[-1] in "()":
#             raise ValueError("Unmatched parentheses")
#         output += stack.pop()
#     return output


# def build_afn(postfix):
#     gen = StateGenerator()
#     stack = []

#     for char in postfix:
#         if char not in '*.|':
#             start = gen.new_state()
#             end = gen.new_state()
#             transitions = {
#                 start: {char: [end]},
#                 end: {}
#             }
#             stack.append((start, end, transitions))

#         elif char == '*':
#             if not stack:
#                 raise ValueError("Syntax error: '*' operator without operand")
#             n_start, n_end, trans = stack.pop()
#             start = gen.new_state()
#             end = gen.new_state()
#             trans.setdefault(start, {}).setdefault("ε", []).extend([n_start, end])
#             trans.setdefault(n_end, {}).setdefault("ε", []).extend([n_start, end])
#             trans.setdefault(end, {})
#             stack.append((start, end, trans))

#         elif char == '.':
#             if len(stack) < 2:
#                 raise ValueError("Syntax error: '.' operator requires two operands")
#             n2_start, n2_end, t2 = stack.pop()
#             n1_start, n1_end, t1 = stack.pop()
#             t1.setdefault(n1_end, {}).setdefault("ε", []).append(n2_start)
#             merged = {**t1, **t2}
#             merged.setdefault(n2_end, {})
#             stack.append((n1_start, n2_end, merged))

#         elif char == '|':
#             if len(stack) < 2:
#                 raise ValueError("Syntax error: '|' operator requires two operands")
#             n2_start, n2_end, t2 = stack.pop()
#             n1_start, n1_end, t1 = stack.pop()
#             start = gen.new_state()
#             end = gen.new_state()
#             merged = {**t1, **t2}
#             merged.setdefault(start, {}).setdefault("ε", []).extend([n1_start, n2_start])
#             merged.setdefault(n1_end, {}).setdefault("ε", []).append(end)
#             merged.setdefault(n2_end, {}).setdefault("ε", []).append(end)
#             merged.setdefault(end, {})
#             stack.append((start, end, merged))

#     if len(stack) != 1:
#         raise ValueError("Invalid postfix expression: remaining elements in stack")

#     return stack[0]


# def thompson_regex_to_epsilon_afn(regex):
#     regex = add_concat_operator(regex)
#     postfix = to_postfix(regex)
#     initial, final, transitions = build_afn(postfix)

#     states = list(transitions.keys())
#     alphabet = sorted(list(set(
#         sym for trans in transitions.values() for sym in trans.keys() if sym != "ε"
#     )))

#     return {
#         "states": states,
#         "alphabet": alphabet + ["ε"],
#         "initial_state": initial,
#         "final_states": [final],
#         "transitions": transitions
#     }

import itertools

class StateGenerator:
    def __init__(self):
        self.counter = 0

    def new_state(self):
        state = f"q{self.counter}"
        self.counter += 1
        return state

class Thompson:
    def __init__(self):
        self.state_gen = StateGenerator()

    def create_basic(self, symbol):
        start = self.state_gen.new_state()
        end = self.state_gen.new_state()
        return {
            "states": [start, end],
            "transitions": {
                start: {symbol: [end]}
            },
            "initial_state": start,
            "final_states": [end]
        }

    def create_epsilon(self):
        return self.create_basic("ε")

    def concatenate(self, a1, a2):
        transitions = {**a1["transitions"]}
        for state, trans in a2["transitions"].items():
            if state in transitions:
                for sym, targets in trans.items():
                    transitions[state].setdefault(sym, []).extend(targets)
            else:
                transitions[state] = trans

        # relier les fins de a1 au début de a2 par ε
        for acc in a1["final_states"]:
            transitions.setdefault(acc, {}).setdefault("ε", []).append(a2["initial_state"])

        return {
            "states": list(set(a1["states"] + a2["states"])),
            "transitions": transitions,
            "initial_state": a1["initial_state"],
            "final_states": a2["final_states"]
        }

    def union(self, a1, a2):
        start = self.state_gen.new_state()
        end = self.state_gen.new_state()
        transitions = {
            start: {"ε": [a1["initial_state"], a2["initial_state"]]},
            **a1["transitions"],
            **a2["transitions"]
        }

        for acc in a1["final_states"] + a2["final_states"]:
            transitions.setdefault(acc, {}).setdefault("ε", []).append(end)

        return {
            "states": list(set([start, end] + a1["states"] + a2["states"])),
            "transitions": transitions,
            "initial_state": start,
            "final_states": [end]
        }

    def kleene_star(self, a):
        start = self.state_gen.new_state()
        end = self.state_gen.new_state()
        transitions = {
            start: {"ε": [a["initial_state"], end]},
            **a["transitions"]
        }

        for acc in a["final_states"]:
            transitions.setdefault(acc, {}).setdefault("ε", []).extend([a["initial_state"], end])

        return {
            "states": list(set([start, end] + a["states"])),
            "transitions": transitions,
            "initial_state": start,
            "final_states": [end]
        }

    def from_postfix(self, postfix):
        stack = []
        for token in postfix:
            if token == ".":
                b = stack.pop()
                a = stack.pop()
                stack.append(self.concatenate(a, b))
            elif token == "+":
                b = stack.pop()
                a = stack.pop()
                stack.append(self.union(a, b))
            elif token == "*":
                a = stack.pop()
                stack.append(self.kleene_star(a))
            else:
                if token == "ε":
                    stack.append(self.create_epsilon())
                else:
                    stack.append(self.create_basic(token))
        return stack[0]  # le NFA final
