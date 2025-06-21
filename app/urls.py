from rest_framework.routers import DefaultRouter
from .views import AutomateViewSet
from django.urls import path, include
from .views import RegexFromEquationsAPIView
from .views import ConvertAFNtoAFDByIdAPIView
from .views import RegexFromAutomateAPIView
from .views  import AFDToAFDCView
from .views import AutomateStateAnalysisView
from .views import AutomateEmondageView
from .views import AFDToRealAFNView
 #=================AJOUT DE STEFAN=======================
from .views import AFNToEpsilonAFNView, EpsilonAFNToAFNView
from .views import EpsilonClosureView
from .views import EpsilonAFNToAFDView
from .views import AFDToEpsilonAFNView
from .views import ThomsomRegexToEpsilonAFNView
from .views import MinimizeAFDView
from .views import RegexToGlushkovAutomateView
from .views import CanonizeAutomateView


router = DefaultRouter()
router.register(r'automates', AutomateViewSet)

urlpatterns = [
    path('', include(router.urls)),
     path('regex/from-equations/', RegexFromEquationsAPIView.as_view()),
      path('automates/<int:automate_id>/convert/', ConvertAFNtoAFDByIdAPIView.as_view()),
      path('automates/<int:automate_id>/to-regex/', RegexFromAutomateAPIView.as_view()),
    path("automates/<int:pk>/complete/", AFDToAFDCView.as_view(), name="afd-to-afdc"),
     path("automates/<int:pk>/to-afn/", AFDToRealAFNView.as_view(), name="afd-to-afn"),
 path("automates/<int:pk>/states-analysis/", AutomateStateAnalysisView.as_view(), name="automate-state-analysis"),
 path("automates/<int:pk>/emondage/", AutomateEmondageView.as_view(), name="automate-emondage"),

 #=================AJOUT DE STEFAN=======================
 path("automates/<int:pk>/to-epsilon-afn/", AFNToEpsilonAFNView.as_view(), name="afn-to-epsilon-afn"),
  path("automates/<int:pk>/from-epsilon-afn/", EpsilonAFNToAFNView.as_view(), name="epsilon-afn-to-afn"),
  path("automates/<int:pk>/epsilon-closure/<str:state_name>/", EpsilonClosureView.as_view(), name="epsilon-closure"),
  path("automates/<int:pk>/from-epsilon-afn-to-afd/", EpsilonAFNToAFDView.as_view(), name="epsilon-afn-to-afd"),
  path("automates/<int:pk>/to-epsilon-afn-from-afd/", AFDToEpsilonAFNView.as_view(), name="afd-to-epsilon-afn"),
  path("automates/<int:pk>/from-regex/", ThomsomRegexToEpsilonAFNView.as_view(), name="regex-to-epsilon-afn"),
  path("automates/<int:pk>/minimize/", MinimizeAFDView.as_view(), name="minimize-afd"),
  path("automates/from-regex-glushkov/", RegexToGlushkovAutomateView.as_view(), name="regex-to-glushkov"), 
  path("automates/<int:pk>/canonize/", CanonizeAutomateView.as_view(), name="canonize-automate"),


]


