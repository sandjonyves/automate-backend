class Position:
    def __init__(self, symbol, index):
        self.symbol = symbol
        self.index = index

    def __repr__(self):
        return f"{self.symbol}_{self.index}"

def parse_regex(regex):
    # Ajout du point pour la concaténation implicite
    result = ''
    for i in range(len(regex)):
        result += regex[i]
        if i + 1 < len(regex):
            if (regex[i].isalnum() or regex[i] == ')') and (regex[i + 1].isalnum() or regex[i + 1] == '('):
                result += '.'
    return result

def to_postfix(regex):
    precedence = {'*': 3, '.': 2, '|': 1}
    output = ''
    stack = []

    for char in regex:
        if char.isalnum():
            output += char
        elif char == '(':
            stack.append(char)
        elif char == ')':
            while stack[-1] != '(':
                output += stack.pop()
            stack.pop()
        else:
            while stack and stack[-1] != '(' and precedence[stack[-1]] >= precedence[char]:
                output += stack.pop()
            stack.append(char)
    while stack:
        output += stack.pop()
    return output

def glushkov(regex):
    regex = parse_regex(regex)
    postfix = to_postfix(regex)
    pos_count = 0
    pos_table = {}
    nullable_stack = []
    firstpos_stack = []
    lastpos_stack = []
    followpos = {}

    for c in postfix:
        if c.isalnum():
            pos = Position(c, pos_count)
            pos_table[pos_count] = pos
            followpos[pos_count] = set()
            nullable_stack.append(False)
            firstpos_stack.append({pos_count})
            lastpos_stack.append({pos_count})
            pos_count += 1
        elif c == '*':
            nullable = True
            firstpos = firstpos_stack.pop()
            lastpos = lastpos_stack.pop()
            nullable_stack.pop()
            for i in lastpos:
                for j in firstpos:
                    followpos[i].add(j)
            nullable_stack.append(True)
            firstpos_stack.append(firstpos)
            lastpos_stack.append(lastpos)
        elif c == '.':
            nullable2 = nullable_stack.pop()
            nullable1 = nullable_stack.pop()
            first2 = firstpos_stack.pop()
            first1 = firstpos_stack.pop()
            last2 = lastpos_stack.pop()
            last1 = lastpos_stack.pop()
            for i in last1:
                for j in first2:
                    followpos[i].add(j)
            nullable_stack.append(nullable1 and nullable2)
            firstpos_stack.append(first1 if not nullable1 else first1 | first2)
            lastpos_stack.append(last2 if not nullable2 else last1 | last2)
        elif c == '|':
            nullable2 = nullable_stack.pop()
            nullable1 = nullable_stack.pop()
            first2 = firstpos_stack.pop()
            first1 = firstpos_stack.pop()
            last2 = lastpos_stack.pop()
            last1 = lastpos_stack.pop()
            nullable_stack.append(nullable1 or nullable2)
            firstpos_stack.append(first1 | first2)
            lastpos_stack.append(last1 | last2)

    nullable = nullable_stack.pop()
    firstpos = firstpos_stack.pop()
    lastpos = lastpos_stack.pop()

    states = [f"q{i}" for i in range(pos_count)]
    transitions = {f"q{i}": {} for i in range(pos_count)}
    for i, followers in followpos.items():
        for j in followers:
            symbol = pos_table[j].symbol
            if symbol not in transitions[f"q{i}"]:
                transitions[f"q{i}"][symbol] = []
            transitions[f"q{i}"][symbol].append(f"q{j}")

    start_state = "start"
    transitions[start_state] = {}
    for i in firstpos:
        symbol = pos_table[i].symbol
        if symbol not in transitions[start_state]:
            transitions[start_state][symbol] = []
        transitions[start_state][symbol].append(f"q{i}")

    final_states = set()
    for i in lastpos:
        final_states.add(f"q{i}")
    if nullable:
        final_states.add(start_state)

    alphabet = sorted(list(set(p.symbol for p in pos_table.values())))

    return {
        "states": [start_state] + states,
        "alphabet": alphabet,
        "initial_state": start_state,
        "final_states": list(final_states),
        "transitions": transitions
    }
