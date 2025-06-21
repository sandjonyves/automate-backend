from rest_framework import serializers
from .models import Automate

class AutomateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Automate
        fields = '__all__'

    def validate(self, data):
        states = data['states']
        initial = data['initial_state']
        finals = data['final_states']
        alphabet = data['alphabet']
        transitions = data['transitions']

        # Vérifie que l'état initial est dans les états
        if initial not in states:
            raise serializers.ValidationError("L'état initial n'est pas dans la liste des états.")

        # Vérifie que les états finaux sont dans les états
        for f in finals:
            if f not in states:
                raise serializers.ValidationError(f"L'état final {f} n'est pas dans la liste des états.")

        # Vérifie que les transitions utilisent des symboles et états valides
        for state, trans in transitions.items():
            if state not in states:
                raise serializers.ValidationError(f"L'état source {state} est inconnu.")
            for symbol, dest in trans.items():
                if symbol not in alphabet:
                    raise serializers.ValidationError(f"Le symbole '{symbol}' n'appartient pas à l'alphabet.")
                # accepte aussi une liste (pour NFA)
                if isinstance(dest, str) and dest not in states:
                    raise serializers.ValidationError(f"L'état destination {dest} est inconnu.")
                elif isinstance(dest, list):
                    for d in dest:
                        if d not in states:
                            raise serializers.ValidationError(f"L'état destination {d} est inconnu.")

        return data


class EquationSystemSerializer(serializers.Serializer):
    equations = serializers.DictField(child=serializers.CharField())
    variable_initiale = serializers.CharField()



class RegexInputSerializer(serializers.Serializer):
    regex = serializers.CharField(max_length=100)



