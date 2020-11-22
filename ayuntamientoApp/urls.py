from django.conf.urls import url,include
from django.urls import path
from rest_framework import routers
#from ayuntamientoApp.views import views
from ayuntamientoApp.apiviews import *

router = routers.DefaultRouter()
#router.register(r'calidadDelAire', views.PublicacionViewSet, basename="Calidad del aire" )

urlpatterns = [
    url(r'^calidadDelAire/$', CalidadDelAireTodo.as_view()),
    url(r'^calidadDelAire/(?P<x>[0-9-.]+),(?P<y>[0-9-.]+)$', CalidadDelAireCoordenadas.as_view()),
    url(r'^calidadDelAire/limit=(?P<limit>[0-9-]+)&skip=(?P<skip>[0-9-]+)$', CalidadDelAirePaginacion.as_view()),
    url(r'^calidadDelAire/limit=(?P<limit>[0-9-]+)$', CalidadDelAirePaginacion.as_view()),
    url(r'^eventos/limit=(?P<limit>[0-9-]+)&skip=(?P<skip>[0-9-]+)$', EventosPaginacion.as_view()),
    url(r'^eventos/limit=(?P<limit>[0-9-]+)$', EventosPaginacion.as_view()),
    path('eventos/<campo>/<contenido>/', Eventos.as_view()),
    path('eventos/<contenido>/', Eventos.as_view()),
    path('eventos/', Eventos.as_view()),
    path('bicis/<latitud>+<longitud>+<rango>/', Bicis.as_view())
]