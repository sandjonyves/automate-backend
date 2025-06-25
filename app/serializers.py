from rest_framework import serializers
from .models import Automate
from .algorithme.is_deterministe import is_deterministic_automaton
class AutomateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automate
        fields = ['id', 'states', 'initial_state', 'final_states', 'alphabet', 'transitions', 'is_deterministic']

    def validate(self, data):
        # automaton_type = data['automaton_type']
        states = data['states']
        initial = data['initial_state']
        finals = data['final_states']
        alphabet = data['alphabet']
        transitions = data['transitions']

        if initial not in states:
            raise serializers.ValidationError("L'état initial n'est pas dans la liste des états.")

        for f in finals:
            if f not in states:
                raise serializers.ValidationError(f"L'état final {f} n'est pas dans la liste des états.")

        for state, trans in transitions.items():
            if state not in states:
                raise serializers.ValidationError(f"L'état source {state} est inconnu.")
            for symbol, dest in trans.items():
                if symbol not in alphabet:
                    raise serializers.ValidationError(f"Le symbole '{symbol}' n'appartient pas à l'alphabet.")
                if isinstance(dest, str):
                    if dest not in states:
                        raise serializers.ValidationError(f"L'état destination {dest} est inconnu.")
                elif isinstance(dest, list):
                    for d in dest:
                        if d not in states:
                            raise serializers.ValidationError(f"L'état destination {d} est inconnu.")

        return data

    def create(self, validated_data):
        validated_data['is_deterministic'] = is_deterministic_automaton(
            validated_data['states'],
            validated_data['alphabet'],
            validated_data['transitions'],
            validated_data['initial_state'],
            validated_data['final_states']
        )
        return super().create(validated_data)
      

    def update(self, instance, validated_data):
        validated_data['is_deterministic'] = validated_data.get('automaton_type') == 'DFA'
        return super().update(instance, validated_data)



class EquationSystemSerializer(serializers.Serializer):
    equations = serializers.DictField(child=serializers.CharField())
    variable_initiale = serializers.CharField()



class RegexInputSerializer(serializers.Serializer):
    regex = serializers.CharField(max_length=100)




# class AutomateSerializer(serializers.Serializer):
#     states = serializers.ListField(child=serializers.CharField())
#     alphabet = serializers.ListField(child=serializers.CharField())
#     transitions = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))
#     initial_state = serializers.CharField()
#     final_states = serializers.ListField(child=serializers.CharField())