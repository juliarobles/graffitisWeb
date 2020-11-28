from django.conf.urls import url,include
from django.urls import path
from rest_framework import routers
#from ayuntamientoApp.views import views
from ayuntamientoApp.apiviews import *

#router = routers.DefaultRouter()
#router.register(r'calidadDelAire', views.PublicacionViewSet, basename="Calidad del aire" )

urlpatterns = [
    url(r'^calidadDelAire/$', CalidadDelAireTodo.as_view()),
    url(r'^calidadDelAire/(?P<x>[0-9-.]+),(?P<y>[0-9-.]+)$', CalidadDelAireCoordenadas.as_view()),
    url(r'^calidadDelAire/(?P<x>[0-9-.]+),(?P<y>[0-9-.]+)&km=(?P<km>[0-9-.]+)$', CalidadDelAireDistancia.as_view()),
    url(r'^calidadDelAire/limit=(?P<limit>[0-9-]+)&skip=(?P<skip>[0-9-]+)$', CalidadDelAirePaginacion.as_view()),
    url(r'^calidadDelAire/limit=(?P<limit>[0-9-]+)$', CalidadDelAirePaginacion2.as_view()),
    url(r'^eventos/limit=(?P<limit>[0-9-]+)&skip=(?P<skip>[0-9-]+)$', EventosPaginacion.as_view()),
    url(r'^eventos/limit=(?P<limit>[0-9-]+)$', EventosPaginacion2.as_view()),
    url(r'eventos/$', EventosTodo.as_view()), 
    url(r'eventos/(?P<campo>[a-zA-Z0-9-_]+)/(?P<contenido>[a-zA-Z0-9-_]+)$', EventosPropiedades.as_view()),
    url(r'eventos/(?P<contenido>[a-zA-Z0-9-_]+)$', EventosContenido.as_view()),
    url(r'eventosID/(?P<pk>[0-9-]+)$', EventosID.as_view()),
    url(r'bicis/$', BicisTodo.as_view()),
    url(r'bicis/(?P<latitud>[0-9-.]+),(?P<longitud>[0-9-.]+)&rango=(?P<rango>[0-9-.]+)$', BicisRango.as_view()),
    url(r'bicis/(?P<id>[^/]+)$', BicisID.as_view())
]
#     path('bicis/<latitud>+<longitud>+<rango>/', Bicis.as_view()),
#     path('bicis/<str:pk>/', Bicis.as_view())
#     path('eventosID/<int:pk>', EventosID.as_view()),
#     path('eventos/<contenido>/', Eventos.as_view()),
#       path('eventos/<campo>/<contenido>/', Eventos.as_view()),
#   path('eventos/', Eventos.as_view()),