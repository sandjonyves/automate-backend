from django.db import models

class Automate(models.Model):
    AUTOMATON_TYPES = [
        ('DFA', 'Déterministe'),
        ('NFA', 'Non Déterministe'),
        ('ε-NFA', 'Epsilon-NFA')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    automaton_type = models.CharField(max_length=10, choices=AUTOMATON_TYPES, default='DFA')

    alphabet = models.JSONField(default=list)
    states = models.JSONField(default=list)
    initial_state = models.CharField(max_length=50)
    final_states = models.JSONField(default=list)
    transitions = models.JSONField(default=dict)
    is_deterministic = models.BooleanField(default=False) 

    def __str__(self):
        return self.name
