from django.conf.urls import url,include
from django.urls import path
from clienteApp.views import *


# Paginas principales
urlpatterns = [
    path('inicio/', inicio, name='inicio'),
    path('principal/', principal, name='principal'),
    path('registro/', registro, name='registro'),
    path('html/eventos/', eventos_list ,name='eventos-list'),
    path('html/eventos/<int:ID_ACTIVIDAD>/', eventos_details ,name='eventos-details'),
    path('html/publicaciones/', list_publicaciones_views, name='publicaciones-list'),
    path('html/publicaciones/detalles/<str:pk>/', publicaciones_detail_view, name='publicacion-detail'),
    path('html/nuevapublicacion/', publicaciones_formulario_view, name='publicacion-formulario'),
    path('html/usuarios', usuarios_list, name='usuarios-list'),
    path('html/usuarios/detalles/<str:pk>/', usuarios_detail, name='usuarios-detail'),
    path('ajax/eventos', cargar_eventos_ajax, name='cargar-eventos-ajax'),
    path('ajax/eventos/<int:ID_ACTIVIDAD>/', cargar_evento_id_ajax, name='cargar-eventos-id'),
]

#Acciones
urlpatterns += [
    path('loginIn', action_login, name='action_login')
]