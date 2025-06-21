from typing import Set, Dict, Tuple
import re

class Glushkov:
    def __init__(self, regex: str):
        self.regex = regex
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.initial_state = 0
        self.final_states = set()
        self.symbol_positions = {}  # Map symbols to their positions in regex
        
    def _get_alphabet(self) -> Set[str]:
        """Extract alphabet from regex"""
        self.alphabet = set(char for char in self.regex if char.isalnum())
        # Map each alphanumeric symbol to its position
        pos = 1
        for i, char in enumerate(self.regex):
            if char.isalnum():
                self.symbol_positions[char + str(i)] = pos
                pos += 1
        return self.alphabet
    
    def _first(self, expr: str) -> Set[int]:
        """Compute FIRST set for regex"""
        if not expr:
            return set()
        if expr[0].isalnum():
            return {self.symbol_positions.get(expr[0] + str(0), 0)}
        if expr[0] == '(':
            count = 1
            i = 1
            while count > 0 and i < len(expr):
                if expr[i] == '(':
                    count += 1
                elif expr[i] == ')':
                    count -= 1
                i += 1
            if i < len(expr) and expr[i] == '*':
                return self._first(expr[1:i-1])
            return self._first(expr[1:i-1]) | (self._first(expr[i:]) if i < len(expr) else set())
        return set()
    
    def _last(self, expr: str) -> Set[int]:
        """Compute LAST set for regex"""
        if not expr:
            return set()
        if expr[-1].isalnum():
            return {self.symbol_positions.get(expr[-1] + str(len(expr)-1), 0)}
        if expr[-1] == ')':
            count = 1
            i = len(expr) - 2
            while count > 0 and i >= 0:
                if expr[i] == ')':
                    count += 1
                elif expr[i] == '(':
                    count -= 1
                i -= 1
            if i >= 0 and expr[i] == '*':
                return self._last(expr[i+1:-1])
            return self._last(expr[i+2:-1]) | (self._last(expr[:i+1]) if i >= 0 else set())
        return set()
    
    def _follow(self, expr: str) -> Dict[int, Set[int]]:
        """Compute FOLLOW sets for regex"""
        follow = {}
        for i in range(len(expr)):
            if expr[i].isalnum():
                state = self.symbol_positions.get(expr[i] + str(i), 0)
                follow.setdefault(state, set())
                if i + 1 < len(expr) and expr[i + 1].isalnum():
                    next_state = self.symbol_positions.get(expr[i + 1] + str(i + 1), 0)
                    follow[state].add(next_state)
                elif i + 1 < len(expr) and expr[i + 1] == '(':
                    count = 1
                    j = i + 2
                    while count > 0 and j < len(expr):
                        if expr[j] == '(':
                            count += 1
                        elif expr[j] == ')':
                            count -= 1
                        j += 1
                    if j < len(expr) and expr[j] == '*':
                        follow[state].update(self._first(expr[i+2:j]))
                    else:
                        follow[state].update(self._first(expr[i+2:j]))
        return follow
    
    def build_automaton(self) -> Tuple[Set[int], Set[str], Dict[Tuple[int, str], Set[int]], int, Set[int]]:
        """Build NFA using Glushkov's algorithm"""
        self.alphabet = self._get_alphabet()
        self.states = set(range(len(self.symbol_positions) + 1))
        
        # Initialize transitions
        for state in self.states:
            self.transitions[state] = {}
            for symbol in self.alphabet:
                self.transitions[state][symbol] = set()
        
        # Compute first, last and follow sets
        first = self._first(self.regex)
        last = self._last(self.regex)
        follow = self._follow(self.regex)
        
        # Set initial and final states
        self.initial_state = 0
        self.final_states = last
        
        # Build transitions
        for symbol, state in self.symbol_positions.items():
            symbol_char = symbol[0]  # Get the actual symbol (e.g., 'a')
            for next_state in follow.get(state, set()):
                self.transitions[state][symbol_char].add(next_state)
        
        # Add transitions from initial state
        for state in first:
            for symbol, pos in self.symbol_positions.items():
                if pos == state:
                    self.transitions[0][symbol[0]].add(state)
        
        return self.states, self.alphabet, self.transitions, self.initial_state, self.final_states