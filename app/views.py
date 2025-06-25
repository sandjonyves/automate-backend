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
# from .algorithme.thompson import thompson_regex_to_epsilon_afn
from .algorithme.glushkov import Glushkov
from .algorithme.minimisation_moore import minimize_moore
from .algorithme.thompson import Thompson
from .algorithme.complement import (
    BaseModelAutomate,
    complement_automate,
    parse_transitions,
    serialize_transitions
)

from .algorithme.union import Automate as UnionAutomate, union_automates
from .algorithme.intersection import Automate as IntersectAutomate, intersect_automates



from .algorithme.concatenation import Automate as ConcatenateAutomate, concatenate_automates



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

        try:
            regex = automate_to_regex(
                states=automate.states,
                initial_state=automate.initial_state,
                final_states=automate.final_states,
                transitions=automate.transitions
            )

            return Response({"regex": regex}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)  


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



class ThompsonFromRegexView(APIView):
    """
    API endpoint to convert a regular expression (in infix notation) into
    an NFA using Thompson's construction algorithm.
    """

    def post(self, request, *args, **kwargs):
        regex_infix = request.data.get("regex")
        if not regex_infix or not isinstance(regex_infix, str):
            return Response(
                {"error": "You must provide a 'regex' as a string."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            postfix_expr = self.infix_to_postfix(regex_infix)
            thompson = Thompson()
            automate = thompson.from_postfix(postfix_expr)
            print(automate)
            return Response({
                "postfix": postfix_expr,
                **automate
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def precedence(self, op):
        if op == '*':
            return 3
        if op == '.':
            return 2
        if op == '+':
            return 1
        return 0

    def is_operator(self, c):
        return c in ['+', '.', '*']

    def insert_concat_symbols(self, expr):
        """
        Ajoute des symboles de concaténation explicites (.) à l'expression.
        Exemple : a(b+c)*d devient a.(b+c)*.d
        """
        result = ""
        for i in range(len(expr)):
            c1 = expr[i]
            result += c1
            if i + 1 < len(expr):
                c2 = expr[i + 1]
                if (c1.isalnum() or c1 == ')' or c1 == '*') and (c2.isalnum() or c2 == '('):
                    result += '.'
        return result

    def infix_to_postfix(self, expr):
        expr = self.insert_concat_symbols(expr.replace(" ", ""))
        output = []
        stack = []

        for token in expr:
            if token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # remove '('
            elif self.is_operator(token):
                while stack and self.precedence(stack[-1]) >= self.precedence(token):
                    output.append(stack.pop())
                stack.append(token)
            else:
                output.append(token)

        while stack:
            output.append(stack.pop())

        return output


# AUTOMATON_TYPE = "NFA"  # ou 'AFN' si tu préfères
# class ThompsonFromRegexView(APIView):
#     """
#     API endpoint: Convert a regex (infix) to a Thompson NFA and save it in DB
#     """

#     def post(self, request, *args, **kwargs):
#         regex_infix = request.data.get("regex")
#         name = request.data.get("name", "Thompson_NFA")

#         if not regex_infix or not isinstance(regex_infix, str):
#             return Response(
#                 {"error": "You must provide 'regex' as a string."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             # 1. Convertir en postfix
#             postfix_expr = self.infix_to_postfix(regex_infix)

#             # 2. Construire l'automate avec Thompson
#             thompson = Thompson()
#             automate_data = thompson.from_postfix(postfix_expr)

#             # 3. Créer et sauvegarder l'automate en DB
#             # automate = Automate.objects.create(
#             #     name=name,
#             #     description=f"Automate généré depuis '{regex_infix}' avec l'algorithme de Thompson.",
#             #     automaton_type=AUTOMATON_TYPE,
#             #     alphabet=list(self.extract_alphabet(postfix_expr)),
#             #     states=automate_data["states"],
#             #     initial_state=automate_data["start_state"],
#             #     final_states=automate_data["accept_states"],
#             #     transitions=automate_data["transitions"],
#             #     is_deterministic=False
#             # )

#             # 4. Répondre au frontend avec les données formatées
#             return Response({
                
#                 "states": automate_data["states"],
#                 "initial_state": automate_data["start_state"],
#                 "final_states": automate_data["accept_states"],
#                 "alphabet": list(self.extract_alphabet(postfix_expr)),
#                 "transitions": automate_data["transitions"]
#             }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     # ------------------------
#     # 🔁 Utilitaires internes
#     # ------------------------

#     def precedence(self, op):
#         return {'*': 3, '.': 2, '+': 1}.get(op, 0)

#     def is_operator(self, c):
#         return c in ['+', '.', '*']

#     def insert_concat_symbols(self, expr):
#         """
#         Ajoute les symboles de concaténation '.' de façon explicite.
#         Exemple : ab devient a.b
#         """
#         result = ""
#         for i in range(len(expr)):
#             c1 = expr[i]
#             result += c1
#             if i + 1 < len(expr):
#                 c2 = expr[i + 1]
#                 if (c1.isalnum() or c1 == ')' or c1 == '*') and (c2.isalnum() or c2 == '('):
#                     result += '.'
#         return result

#     def infix_to_postfix(self, expr):
#         expr = self.insert_concat_symbols(expr.replace(" ", ""))
#         output, stack = [], []

#         for token in expr:
#             if token == '(':
#                 stack.append(token)
#             elif token == ')':
#                 while stack and stack[-1] != '(':
#                     output.append(stack.pop())
#                 stack.pop()
#             elif self.is_operator(token):
#                 while stack and self.precedence(stack[-1]) >= self.precedence(token):
#                     output.append(stack.pop())
#                 stack.append(token)
#             else:
#                 output.append(token)

#         while stack:
#             output.extend(reversed(stack))
#         return output

#     def extract_alphabet(self, postfix):
#         return set(c for c in postfix if c.isalnum())



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
        # except Exception as e:
        #     return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        







from collections import defaultdict

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
            
            def parse_transitions(transitions_dict):
                transitions = {}
                for state, trans_map in transitions_dict.items():
                    if isinstance(trans_map, dict):
                        for symbol, dest_list in trans_map.items():
                            key = (state, symbol)
                            if isinstance(dest_list, list):
                                transitions[key] = set(dest_list)
                            else:
                                transitions[key] = {dest_list}
                    else:
                        print(f"Warning: transitions for state {state} is not a dict")
                return transitions
            
            automate1_transitions = parse_transitions(automate1_instance.transitions)
            automate2_transitions = parse_transitions(automate2_instance.transitions)

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

            def transitions_to_nested_dict(transitions):
                result = defaultdict(lambda: defaultdict(list))
                for (state, symbol), next_states in transitions.items():
                    result[state][symbol].extend(next_states)
                return {state: dict(symbols) for state, symbols in result.items()}
            
            response_data = {
                'states': list(intersect_automate.states),
                'alphabet': list(intersect_automate.alphabet),
                'transitions': transitions_to_nested_dict(intersect_automate.transitions),
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
class ComplementAutomateView(APIView):
    def post(self, request):
        try:
            automate_id = request.data.get("automate_id")
            if not automate_id:
                return Response({"error": "automate_id is required"}, status=status.HTTP_400_BAD_REQUEST)

            automate_instance = Automate.objects.get(pk=automate_id)

            parsed_transitions = parse_transitions(automate_instance.transitions)

            automate = BaseModelAutomate(
                states=set(automate_instance.states),
                alphabet=set(automate_instance.alphabet),
                transitions=parsed_transitions,
                initial_state=automate_instance.initial_state,
                final_states=set(automate_instance.final_states)
            )

            complemented = complement_automate(automate)

            response_data = {
                "states": list(complemented.states),
                "alphabet": list(complemented.alphabet),
                "initial_state": complemented.initial_state,
                "final_states": list(complemented.final_states),
                "transitions": serialize_transitions(complemented.transitions)
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Automate not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConcatenateAutomateView(APIView):
    def post(self, request):
        try:
            automate_id1 = request.data.get("automate_id1")
            automate_id2 = request.data.get("automate_id2")

            if not automate_id1 or not automate_id2:
                return Response({"error": "Both automate_id1 and automate_id2 are required"},
                                status=status.HTTP_400_BAD_REQUEST)

            automate1_instance = Automate.objects.get(pk=automate_id1)
            automate2_instance = Automate.objects.get(pk=automate_id2)

            def parse_transitions(transitions_dict):
                transitions = {}
                for state, trans_map in transitions_dict.items():
                    if isinstance(trans_map, dict):
                        for symbol, targets in trans_map.items():
                            transitions[(state, symbol)] = set(targets) if isinstance(targets, list) else {targets}
                return transitions

            automate1 = Automate(
                states=set(automate1_instance.states),
                alphabet=set(automate1_instance.alphabet),
                transitions=parse_transitions(automate1_instance.transitions),
                initial_state=automate1_instance.initial_state,
                final_states=set(automate1_instance.final_states)
            )

            automate2 = Automate(
                states=set(automate2_instance.states),
                alphabet=set(automate2_instance.alphabet),
                transitions=parse_transitions(automate2_instance.transitions),
                initial_state=automate2_instance.initial_state,
                final_states=set(automate2_instance.final_states)
            )

            result = concatenate_automates(automate1, automate2)

            # Convertir transitions (tuple key) => { state: { symbol: [states] } }
            def convert_transitions(trans_dict):
                formatted = defaultdict(lambda: defaultdict(list))
                for (state, symbol), targets in trans_dict.items():
                    formatted[state][symbol].extend(targets)
                return {state: dict(symbols) for state, symbols in formatted.items()}

            response_data = {
                'states': list(result.states),
                'alphabet': list(result.alphabet),
                'transitions': convert_transitions(result.transitions),
                'initial_state': result.initial_state,
                'final_states': list(result.final_states)
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "One or both automates not found"},
                            status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)