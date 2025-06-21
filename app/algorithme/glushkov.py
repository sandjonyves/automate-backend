from typing import Set, Dict, Tuple, List, Optional

class RegexNode:
    def __init__(self, kind: str, children: Optional[List['RegexNode']] = None, symbol: Optional[str] = None):
        self.kind = kind  # 'union', 'concat', 'star', 'sym'
        self.children = children or []
        self.symbol = symbol

    def __repr__(self):
        if self.kind == 'sym':
            return f"Sym({self.symbol})"
        return f"{self.kind}({self.children})"

class RegexParser:
    def __init__(self, regex: str):
        self.regex = regex
        self.pos = 0
        self.length = len(regex)

    def parse(self) -> RegexNode:
        node = self.parse_union()
        if self.pos < self.length:
            raise ValueError(f"Unexpected character at position {self.pos}: '{self.regex[self.pos]}'")
        return node

    def parse_union(self) -> RegexNode:
        left = self.parse_concat()
        while self.pos < self.length and self.regex[self.pos] == '+':
            self.pos += 1
            right = self.parse_concat()
            left = RegexNode('union', [left, right])
        return left

    def parse_concat(self) -> RegexNode:
        nodes = []
        while self.pos < self.length and self.regex[self.pos] not in ')+':
            nodes.append(self.parse_star())
        if not nodes:
            return RegexNode('sym', symbol='ε')
        if len(nodes) == 1:
            return nodes[0]
        return RegexNode('concat', nodes)

    def parse_star(self) -> RegexNode:
        node = self.parse_atom()
        while self.pos < self.length and self.regex[self.pos] == '*':
            self.pos += 1
            node = RegexNode('star', [node])
        return node

    def parse_atom(self) -> RegexNode:
        if self.pos >= self.length:
            return RegexNode('sym', symbol='ε')
        c = self.regex[self.pos]
        if c == '(':
            self.pos += 1
            node = self.parse_union()
            if self.pos >= self.length or self.regex[self.pos] != ')':
                raise ValueError("Missing closing parenthesis")
            self.pos += 1
            return node
        elif c.isalnum():
            self.pos += 1
            return RegexNode('sym', symbol=c)
        else:
            raise ValueError(f"Unexpected character '{c}' at position {self.pos}")

class Glushkov:
    def __init__(self, regex: str):
        self.regex = regex
        self.parser = RegexParser(regex)
        self.ast = self.parser.parse()
        self.positions = dict()  # position index -> symbol
        self.pos_count = 0
        self.firstpos = set()
        self.lastpos = set()
        self.followpos = dict()
        self.states = set()
        self.alphabet = set()
        self.transitions = dict()
        self.initial_state = "q0"
        self.final_states = set()

    def _assign_positions(self, node: RegexNode):
        if node.kind == 'sym':
            if node.symbol != 'ε':
                self.pos_count += 1
                self.positions[self.pos_count] = node.symbol
            return
        for child in node.children:
            self._assign_positions(child)

    def _firstpos(self, node: RegexNode) -> Set[int]:
        if node.kind == 'sym':
            if node.symbol == 'ε':
                return set()
            for pos, sym in self.positions.items():
                if sym == node.symbol:
                    return {pos}
            return set()
        elif node.kind == 'union':
            return self._firstpos(node.children[0]) | self._firstpos(node.children[1])
        elif node.kind == 'concat':
            left_first = self._firstpos(node.children[0])
            if self._nullable(node.children[0]):
                return left_first | self._firstpos(node.children[1])
            else:
                return left_first
        elif node.kind == 'star':
            return self._firstpos(node.children[0])
        return set()

    def _lastpos(self, node: RegexNode) -> Set[int]:
        if node.kind == 'sym':
            if node.symbol == 'ε':
                return set()
            for pos, sym in self.positions.items():
                if sym == node.symbol:
                    return {pos}
            return set()
        elif node.kind == 'union':
            return self._lastpos(node.children[0]) | self._lastpos(node.children[1])
        elif node.kind == 'concat':
            right_last = self._lastpos(node.children[1])
            if self._nullable(node.children[1]):
                return right_last | self._lastpos(node.children[0])
            else:
                return right_last
        elif node.kind == 'star':
            return self._lastpos(node.children[0])
        return set()

    def _nullable(self, node: RegexNode) -> bool:
        if node.kind == 'sym':
            return node.symbol == 'ε'
        elif node.kind == 'union':
            return self._nullable(node.children[0]) or self._nullable(node.children[1])
        elif node.kind == 'concat':
            return self._nullable(node.children[0]) and self._nullable(node.children[1])
        elif node.kind == 'star':
            return True
        return False

    def _compute_followpos(self, node: RegexNode):
        if node.kind == 'concat':
            lastpos_left = self._lastpos(node.children[0])
            firstpos_right = self._firstpos(node.children[1])
            for p in lastpos_left:
                self.followpos.setdefault(p, set()).update(firstpos_right)
            self._compute_followpos(node.children[0])
            self._compute_followpos(node.children[1])
        elif node.kind == 'star':
            lastpos_node = self._lastpos(node.children[0])
            firstpos_node = self._firstpos(node.children[0])
            for p in lastpos_node:
                self.followpos.setdefault(p, set()).update(firstpos_node)
            self._compute_followpos(node.children[0])
        elif node.kind in ('union', 'sym'):
            for child in node.children:
                self._compute_followpos(child)

    def build_automaton(self) -> Tuple[Set[str], Set[str], Dict[str, Dict[str, Set[str]]], str, Set[str]]:
        self._assign_positions(self.ast)

        self.firstpos = self._firstpos(self.ast)
        self.lastpos = self._lastpos(self.ast)
        self.followpos = dict()
        self._compute_followpos(self.ast)

        self.states = {"q0"}
        for pos in self.positions:
            self.states.add(f"q{pos}")

        self.alphabet = set(self.positions.values())
        self.initial_state = "q0"
        self.final_states = {f"q{pos}" for pos in self.lastpos}

        self.transitions = {state: dict() for state in self.states}

        for pos in self.firstpos:
            symbol = self.positions[pos]
            self.transitions["q0"].setdefault(symbol, set()).add(f"q{pos}")

        for pos, next_positions in self.followpos.items():
            symbol = self.positions[pos]
            for np in next_positions:
                symbol_next = self.positions[np]
                self.transitions[f"q{pos}"].setdefault(symbol_next, set()).add(f"q{np}")

        # Supprimer états inaccessibles
        self._remove_unreachable_states()

        return self.states, self.alphabet, self.transitions, self.initial_state, self.final_states

    def _remove_unreachable_states(self):
        reachable = set()
        to_visit = {self.initial_state}

        while to_visit:
            state = to_visit.pop()
            if state not in reachable:
                reachable.add(state)
                for symbol, dests in self.transitions.get(state, {}).items():
                    for dest in dests:
                        if dest not in reachable:
                            to_visit.add(dest)

        # Filtrer transitions
        new_transitions = {}
        for state in reachable:
            new_transitions[state] = {}
            for symbol, dests in self.transitions.get(state, {}).items():
                filtered = {d for d in dests if d in reachable}
                if filtered:
                    new_transitions[state][symbol] = filtered

        # Filtrer états finaux
        new_final_states = self.final_states.intersection(reachable)

        # Mettre à jour
        self.states = reachable
        self.transitions = new_transitions
        self.final_states = new_final_states

# Exemple d'utilisation :

if __name__ == "__main__":
    regex = "(a+b)*ba"
    glushkov = Glushkov(regex)
    states, alphabet, transitions, initial_state, final_states = glushkov.build_automaton()

    print("States:", states)
    print("Alphabet:", alphabet)
    print("Initial State:", initial_state)
    print("Final States:", final_states)
    print("Transitions:")
    for state, trans in transitions.items():
        print(f" {state}: {trans}")
