from rest_framework.routers import DefaultRouter
from .views import AutomateViewSet
from django.urls import path, include
from .views import RegexFromEquationsAPIView
from .views import ConvertAFNtoAFDByIdAPIView
from .views import RegexFromAutomateAPIView
from .views  import AFDToAFDCView
from .views import AutomateStateAnalysisView
from .views import AutomateEmondageView
router = DefaultRouter()
router.register(r'automates', AutomateViewSet)

urlpatterns = [
    path('', include(router.urls)),
     path('regex/from-equations/', RegexFromEquationsAPIView.as_view()),
      path('automates/<int:automate_id>/convert/', ConvertAFNtoAFDByIdAPIView.as_view()),
      path('automates/<int:automate_id>/to-regex/', RegexFromAutomateAPIView.as_view()),
    path("automates/<int:pk>/complete/", AFDToAFDCView.as_view(), name="afd-to-afdc"),
 path("automates/<int:pk>/states-analysis/", AutomateStateAnalysisView.as_view(), name="automate-state-analysis"),
 path("automates/<int:pk>/emondage/", AutomateEmondageView.as_view(), name="automate-emondage"),
]
