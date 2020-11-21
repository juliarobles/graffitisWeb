from django.conf.urls import url,include
from rest_framework import routers
#from ayuntamientoApp.views import views
from ayuntamientoApp.apiviews import CalidadDelAireTodo, CalidadDelAireCoordenadas

router = routers.DefaultRouter()
#router.register(r'calidadDelAire', views.PublicacionViewSet, basename="Calidad del aire" )

urlpatterns = [
    url(r'^calidadDelAire/$', CalidadDelAireTodo.as_view()),
    url(r'^calidadDelAire/(?P<x>[a-zA-Z0-9-.]+),(?P<y>[a-zA-Z0-9-.]+)$', CalidadDelAireCoordenadas.as_view()),
]