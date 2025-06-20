from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Automate
from .serializers import AutomateSerializer
from .serializers import EquationSystemSerializer
from .serializers import AutomateSerializer
from .serializers import RegexInputSerializer
from .algorithme.afn_to_afd import afn_to_afd
from .algorithme.equation_to_regex import arden_resolution
from .algorithme.automate_to_regex import automate_to_regex
from .algorithme.afd_to_afdc import afd_to_afdc
from .algorithme.automate_analysis import identify_states
from .algorithme.automate_emondage import emonder_automate
from .algorithme.epsilon_conversion import afn_to_epsilon_afn, epsilon_afn_to_afn
from .algorithme.epsilon_closure import epsilon_closure
from .algorithme.afd_to_afn import afd_to_afn
from .algorithme.epsilon_closure import epsilon_closure
from .algorithme.epsilon_afn_to_afd import epsilon_afn_to_afd
from .algorithme.afd_to_epsilon_afn import afd_to_epsilon_afn
from .algorithme.thompson import thompson_regex_to_epsilon_afn
from .algorithme.glushkov import Glushkov
from .algorithme.minimisation_moore import minimize_moore

from .algorithme.union import Automate as UnionAutomate, union_automates
from .algorithme.intersection import Automate as IntersectAutomate, intersect_automates

from .algorithme.complement import Automate as  complement_automate

from .algorithme.concatenation import concatenate_automata, Automate





class AutomateViewSet(viewsets.ModelViewSet):
    queryset = Automate.objects.all()
    serializer_class = AutomateSerializer



class RegexFromEquationsAPIView(APIView):
    def post(self, request):
        serializer = EquationSystemSerializer(data=request.data)
        if serializer.is_valid():
            equations = serializer.validated_data["equations"]
            variable_initiale = serializer.validated_data["variable_initiale"]

            try:
                regex = arden_resolution(equations, variable_initiale)
                print(regex)
                return Response({"expression_reguliere": regex})
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        return Response(serializer.errors, status=400)






class ConvertAFNtoAFDByIdAPIView(APIView):
    def post(self, request, automate_id):
        try:
            automate = Automate.objects.get(id=automate_id)
        except Automate.DoesNotExist:
            return Response({"error": "Automate non trouvé."}, status=404)

        if automate.is_deterministic:
            return Response({"message": "Cet automate est déjà un AFD."})

        try:
            afd_data = afn_to_afd(
                alphabet=automate.alphabet,
                states=automate.states,
                initial_state=automate.initial_state,
                final_states=automate.final_states,
                transitions=automate.transitions
            )
            return Response({
                "message": "Conversion réussie.",
                "afd": afd_data
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)






class RegexFromAutomateAPIView(APIView):
    def post(self, request, automate_id):
        try:
            automate = Automate.objects.get(id=automate_id)
        except Automate.DoesNotExist:
            return Response({"error": "Automate non trouvé."}, status=404)
        print(automate)
        # try:
        expression = automate_to_regex(
                states=automate.states,
                initial_state=automate.initial_state,
                final_states=automate.final_states,
                transitions=automate.transitions
            )
        return Response({"regex": expression})
        # except Exception as e:
        #     return Response({"error": str(e)}, status=400)



class AFDToAFDCView(APIView):
    def post(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=status.HTTP_404_NOT_FOUND)

        if not automate.is_deterministic:
            return Response({"error": "Automaton must be deterministic (AFD)."}, status=400)

        # Appel de l'algorithme de complétion
        result = afd_to_afdc(
            states=automate.states,
            alphabet=automate.alphabet,
            transitions=automate.transitions
        )

        # Réponse complète avec les champs attendus par le frontend
        return Response({
            "states": result["states"],
            "alphabet": result["alphabet"],
            "transitions": result["transitions"],
            "sink_state": result["sink_state"],
            "initial_state": automate.initial_state,
            "final_states": automate.final_states
        }, status=200)
    

    
class AutomateStateAnalysisView(APIView):
    def get(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        result = identify_states(
            states=automate.states,
            initial_state=automate.initial_state,
            final_states=automate.final_states,
            transitions=automate.transitions
        )

        return Response(result, status=200)



class AutomateEmondageView(APIView):
    def post(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        result = emonder_automate(
            states=automate.states,
            initial_state=automate.initial_state,
            final_states=automate.final_states,
            transitions=automate.transitions,
            alphabet=automate.alphabet
        )

        return Response(result, status=200)
    




    
 #=================AJOUT DE STEFAN=======================

class AFNToEpsilonAFNView(APIView):
    def post(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        if automate.is_deterministic:
            return Response({"error": "Must be an AFN to convert to epsilon-AFN."}, status=400)

        result = afn_to_epsilon_afn(
            
            states=automate.states,
            transitions=automate.transitions
        )

        return Response({
            "states": automate.states,
            "alphabet": automate.alphabet,
            "initial_state": automate.initial_state,
            "final_states": automate.final_states,
            "transitions": result
        }, status=200)


class AFDToRealAFNView(APIView):
    def post(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        # if not automate.is_deterministic:
        #     return Response({"error": "Automate must be deterministic (AFD)."}, status=400)

        result = afd_to_afn(
            states=automate.states,
            alphabet=automate.alphabet,
            transitions=automate.transitions,
            initial_state=automate.initial_state,
            final_states=automate.final_states
        )

        return Response(result, status=200)



class EpsilonAFNToAFNView(APIView):
    def post(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        if automate.is_deterministic:
            return Response({"error": "Not an epsilon-AFN (automate already deterministic)."}, status=400)

        # Conversion de l'epsilon-AFN en AFN
        result = epsilon_afn_to_afn(
            states=automate.states,
            alphabet=automate.alphabet,
            transitions=automate.transitions.get("transitions", automate.transitions)
        )

        return Response({
            "states": automate.states,
            "alphabet": [a for a in automate.alphabet if a != "ε"],
            "initial_state": automate.initial_state,
            "final_states": automate.final_states,
            "transitions": result
        }, status=200)




class EpsilonClosureView(APIView):
    def get(self, request, pk, state_name):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        if "ε" not in [str(a) for a in automate.alphabet]:
            return Response({"error": "This automate has no ε-transitions."}, status=400)

        state_name = str(state_name)
        if state_name not in [str(s) for s in automate.states]:
            return Response({"error": f"State '{state_name}' not found in automate."}, status=404)

        closure = epsilon_closure(state_name, automate.transitions)
        return Response({
            "state": state_name,
            "epsilon_closure": closure
        }, status=200)
    





class EpsilonAFNToAFDView(APIView):
    def post(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        if automate.is_deterministic:
            return Response({"error": "This automate is already deterministic."}, status=400)

        if "ε" not in automate.alphabet:
            return Response({"error": "This automate has no ε-transitions to eliminate."}, status=400)

        result = epsilon_afn_to_afd(
            states=automate.states,
            alphabet=automate.alphabet,
            transitions=automate.transitions,
            initial_state=automate.initial_state,
            final_states=automate.final_states
        )

        return Response(result, status=200)
    



class AFDToEpsilonAFNView(APIView):
    def post(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        if not automate.is_deterministic:
            return Response({"error": "This automate is not deterministic (AFD required)."}, status=400)

        result = afd_to_epsilon_afn(
            states=automate.states,
            alphabet=automate.alphabet,
            transitions=automate.transitions
        )

        return Response({
            "states": automate.states,
            "alphabet": automate.alphabet + ["ε"] if "ε" not in automate.alphabet else automate.alphabet,
            "initial_state": automate.initial_state,
            "final_states": automate.final_states,
            "transitions": result
        }, status=200)
    


# thomsom pure
class RegexToEpsilonAFNView(APIView): 
    def post(self, request):
        regex = request.data.get("regex")
        if not regex:
            return Response({"error": "No regex provided."}, status=400)
        try:
            result = thompson_regex_to_epsilon_afn(regex)
            return Response(result, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)




class MinimizeAFDView(APIView):
    def post(self, request, pk):
        try:
            automate = Automate.objects.get(pk=pk)
        except Automate.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        if not automate.is_deterministic:
            return Response({"error": "This automate is not deterministic. Minimization requires an AFD."}, status=400)

        result = minimize_moore(
            states=automate.states,
            alphabet=automate.alphabet,
            initial_state=automate.initial_state,
            final_states=automate.final_states,
            transitions=automate.transitions
        )

        return Response(result, status=200)
    




import json

class AutomatonGlushkov(APIView):
    def post(self, request):
        regex = request.data.get('regex')
        if not regex:
            return Response({'error': 'Regex is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            glushkov = Glushkov(regex)
            states, alphabet, transitions, initial_state, final_states = glushkov.build_automaton()
            
            # Convert sets to lists for JSON serialization
            response_data = {
                'states': list(states),
                'alphabet': list(alphabet),
                'transitions': {
                    str(state): {
                        symbol: list(targets) 
                        for symbol, targets in transitions[state].items() 
                        if targets
                    } 
                    for state in transitions
                },
                'initial_state': initial_state,
                'final_states': list(final_states)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)







from .algorithme.canonisation import CanonicalAutomate,canonize

from django.core.exceptions import ObjectDoesNotExist

from typing import Set, Dict, Tuple
from collections import defaultdict
from queue import Queue

# Assure-toi d'importer ton modèle Automate ici
from .models import Automate

def parse_automate_json(data: dict) -> CanonicalAutomate:
    states = set(data["states"])
    alphabet = set(data["alphabet"])
    initial_state = data["initial_state"]
    final_states = set(data["final_states"])
    
    transitions = {}
    raw_transitions = data["transitions"]
    
    for state, trans in raw_transitions.items():
        for symbol, dest in trans.items():
            if isinstance(dest, list):
                transitions[(state, symbol)] = set(dest)
            else:
                transitions[(state, symbol)] = {dest}

    return CanonicalAutomate(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        initial_state=initial_state,
        final_states=final_states
    )


class CanonicalAutomate:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict[Tuple[str, str], Set[str]], 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states

# Utilitaire pour parser les transitions au bon format
def parse_transitions(raw_transitions: dict) -> Dict[Tuple[str, str], Set[str]]:
    parsed = {}
    for from_state, transitions_for_state in raw_transitions.items():
        for symbol, dest in transitions_for_state.items():
            if isinstance(dest, list):
                parsed[(from_state, symbol)] = set(dest)
            else:
                parsed[(from_state, symbol)] = {dest}
    return parsed


class CanonizeAutomateView(APIView):
    def get(self, request, pk):
        try:
            # Récupération de l'automate depuis la base de données
            automate_instance = Automate.objects.get(pk=pk)

            # Création de l'automate canonique (via JSONField, pas besoin de eval !)
            automate = CanonicalAutomate(
                states=set(automate_instance.states),
                alphabet=set(automate_instance.alphabet),
                transitions=parse_transitions(automate_instance.transitions),
                initial_state=automate_instance.initial_state,
                final_states=set(automate_instance.final_states)
            )

            # Canonisation
            canonized_automate = canonize(automate)

            # Sérialisation des transitions pour les rendre compatibles JSON
            transitions_serialized = {}
            for (from_state, symbol), to_states in canonized_automate.transitions.items():
                if from_state not in transitions_serialized:
                    transitions_serialized[from_state] = {}
                transitions_serialized[from_state][symbol] = list(to_states)

            # Réponse à envoyer
            response_data = {
                'states': list(canonized_automate.states),
                'alphabet': list(canonized_automate.alphabet),
                'transitions': transitions_serialized,
                'initial_state': canonized_automate.initial_state,
                'final_states': list(canonized_automate.final_states)
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'error': 'Automate not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class UnionAutomateView(APIView):
    def post(self, request):
        try:
            # Récupérer les IDs des automates depuis la requête
            automate_id1 = request.data.get("automate_id1")
            automate_id2 = request.data.get("automate_id2")
            print(request.data)
            # if not automate_id1 or not automate_id2:
            #     return Response({"error": "Both automate_id1 and automate_id2 are required"}, 
            #                   status=status.HTTP_400_BAD_REQUEST)

            # Récupérer les automates depuis la base de données
            automate1_instance = Automate.objects.get(pk=automate_id1)
            automate2_instance = Automate.objects.get(pk=automate_id2)
            
            # Convertir en objets Automate pour le traitement
            automate1 = UnionAutomate(
                states=set(automate1_instance.states),
                alphabet=set(automate1_instance.alphabet),
                transitions=automate1_instance.transitions,
                initial_state=automate1_instance.initial_state,
                final_states=set(automate1_instance.final_states)
            )
            automate2 = UnionAutomate(
                states=set(automate2_instance.states),
                alphabet=set(automate2_instance.alphabet),
                transitions=automate2_instance.transitions,
                initial_state=automate2_instance.initial_state,
                final_states=set(automate2_instance.final_states)
            )
            
            print(automate1.transitions,automate2.transitions)
            # Calculer l'union
            union_automate = union_automates(automate1, automate2)
            
            # Préparer la réponse
            response_data = {
                'states': list(union_automate.states),
                'alphabet': list(union_automate.alphabet),
                'transitions': union_automate.transitions,
                'initial_state': union_automate.initial_state,
                'final_states': list(union_automate.final_states)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({"error": "One or both automates not found"}, 
                          status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        







class IntersectAutomateView(APIView):
    def post(self, request):
        try:
            automate_id1 = request.data.get("automate_id1")
            automate_id2 = request.data.get("automate_id2")
            
            if not automate_id1 or not automate_id2:
                return Response({"error": "Both automate_id1 and automate_id2 are required"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            automate1_instance = Automate.objects.get(pk=automate_id1)
            automate2_instance = Automate.objects.get(pk=automate_id2)
            
            # Convertir les transitions en tuples, gérer les cas où les clés ne sont pas des tuples
            def parse_transitions(transitions_dict):
                transitions = {}
                for key, value in transitions_dict.items():
                    if isinstance(key, str):
                        # Supposer que la clé est au format "etat_symbole" (ex: "q0_a")
                        if "_" in key:
                            state, symbol = key.split("_")
                            transitions[(state, symbol)] = set(value) if isinstance(value, list) else {value}
                        else:
                            print(f"Warning: Invalid transition key format: {key}")
                    elif isinstance(key, tuple) and len(key) == 2:
                        transitions[key] = set(value) if isinstance(value, list) else {value}
                    else:
                        print(f"Warning: Skipping invalid key: {key}")
                return transitions

            automate1_transitions = parse_transitions(automate1_instance.transitions)
            automate2_transitions = parse_transitions(automate2_instance.transitions)
            print(f"Automate1 transitions: {automate1_transitions}")
            print(f"Automate2 transitions: {automate2_transitions}")

            automate1 = IntersectAutomate(
                states=set(automate1_instance.states),
                alphabet=set(automate1_instance.alphabet),
                transitions=automate1_transitions,
                initial_state=automate1_instance.initial_state,
                final_states=set(automate1_instance.final_states)
            )
            automate2 = IntersectAutomate(
                states=set(automate2_instance.states),
                alphabet=set(automate2_instance.alphabet),
                transitions=automate2_transitions,
                initial_state=automate2_instance.initial_state,
                final_states=set(automate2_instance.final_states)
            )
            
            intersect_automate = intersect_automates(automate1, automate2)
            
            response_data = {
                'states': list(intersect_automate.states),
                'alphabet': list(intersect_automate.alphabet),
                'transitions': {k: list(v) for k, v in intersect_automate.transitions.items()},
                'initial_state': intersect_automate.initial_state,
                'final_states': list(intersect_automate.final_states)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({"error": "One or both automates not found"}, 
                          status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

def complement_automate(automate: Automate) -> Automate:
    """Calcule le complémentaire d'un automate en inversant les états finaux/non finaux."""
    new_final_states = automate.states - automate.final_states
    print(f"New final states (old non-final states): {new_final_states}")

    return Automate(
        states=automate.states,
        alphabet=automate.alphabet,
        transitions=automate.transitions,
        initial_state=automate.initial_state,
        final_states=new_final_states
    )

class ComplementAutomateView(APIView):
    def post(self, request):
        try:
            print("Starting ComplementAutomateView processing")
            automate_id = request.data.get("automate_id")
            print(f"Received automate_id: {automate_id}")
            
            if not automate_id:
                return Response({"error": "automate_id is required"}, 
                              status=status.HTTP_400_BAD_REQUEST)

            automate_instance = Automate.objects.get(pk=automate_id)
            print(f"Fetched automate instance: {automate_instance.__dict__}")
            
            def parse_transitions(transitions_dict):
                transitions = {}
                print(f"Parsing transitions: {transitions_dict}")
                for key, value in transitions_dict.items():
                    print(f"Processing key: {key}, value: {value}")
                    if isinstance(key, str):
                        if "_" in key:
                            state, symbol = key.split("_")
                            transitions[(state, symbol)] = set(value) if isinstance(value, list) else {value}
                        else:
                            print(f"Warning: Invalid transition key format: {key}")
                    elif isinstance(key, tuple) and len(key) == 2:
                        transitions[key] = set(value) if isinstance(value, list) else {value}
                    else:
                        print(f"Warning: Skipping invalid key: {key}")
                print(f"Parsed transitions: {transitions}")
                return transitions

            automate_transitions = parse_transitions(automate_instance.transitions)
            print(f"Automate transitions after parsing: {automate_transitions}")

            # Création de l'objet Automate (pas ComplementAutomate)
            automate = Automate(
                states=set(automate_instance.states),
                alphabet=set(automate_instance.alphabet),
                transitions=automate_transitions,
                initial_state=automate_instance.initial_state,
                final_states=set(automate_instance.final_states)
            )
            print(f"Automate object created: {automate.__dict__}")
            
            # Appel de la fonction complement_automate (pas de classe)
            complemented = complement_automate(automate)
            print(f"Complemented automate created: {complemented.final_states}")

            response_data = {
                'states': list(complemented.states),
                'alphabet': list(complemented.alphabet),
                'transitions': {str(k): list(v) for k, v in complemented.transitions.items()},
                'initial_state': complemented.initial_state,
                'final_states': list(complemented.final_states)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ObjectDoesNotExist:
            return Response({"error": "Automate not found"}, 
                          status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


