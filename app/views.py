from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Automate
from .serializers import AutomateSerializer
from .serializers import EquationSystemSerializer
from .serializers import AutomateSerializer
from .algorithme.afn_to_afd import afn_to_afd
from .algorithme.equation_to_regex import arden_resolution
from .algorithme.automate_to_regex import automate_to_regex
from .algorithme.afd_to_afdc import afd_to_afdc
from .algorithme.automate_analysis import identify_states
from .algorithme.automate_emondage import emonder_automate
from .algorithme.epsilon_conversion import afn_to_epsilon_afn, epsilon_afn_to_afn
from app.algorithme.epsilon_closure import epsilon_closure
from .algorithme.afd_to_afn import afd_to_afn
from .algorithme.epsilon_closure import epsilon_closure
from .algorithme.epsilon_afn_to_afd import epsilon_afn_to_afd
from .algorithme.afd_to_epsilon_afn import afd_to_epsilon_afn
from .algorithme.thompson import thompson_regex_to_epsilon_afn
from .algorithme.minimisation_moore import minimize_moore
from .algorithme.glushkov import glushkov
from .algorithme.canonisation import canonize_automate




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
            initial_states=automate.initial_state,
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

        result = epsilon_afn_to_afn(
            states=automate.states,
            alphabet=automate.alphabet,
            transitions=automate.transitions
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
    



class ThomsomRegexToEpsilonAFNView(APIView):
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
    


class RegexToGlushkovAutomateView(APIView):
    def post(self, request):
        regex = request.data.get("regex")
        if not regex:
            return Response({"error": "regex is required."}, status=400)
        try:
            result = glushkov(regex)
            return Response(result, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        





class CanonizeAutomateView(APIView):
    def post(self, request, pk):
        try:
            automate = Automata.objects.get(pk=pk)
        except Automata.DoesNotExist:
            return Response({"error": "Automate not found."}, status=404)

        result = canonize_automate(
            states=automate.states,
            alphabet=automate.alphabet,
            initial_state=automate.initial_state,
            final_states=automate.final_states,
            transitions=automate.transitions,
            is_deterministic=automate.is_deterministic
        )

        return Response(result, status=200)