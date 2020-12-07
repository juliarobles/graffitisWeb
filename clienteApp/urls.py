from django.conf.urls import url,include
from django.urls import path
from clienteApp.views.views import *
from clienteApp.views.loginViews import *

#  ** Información API IMGUR**
#  ** Cuenta: graffitisweb@gmail.com
#  ** Pass: graffiti1$
#  **  client_id = '6f71c692857b528'
#  **  client_secret = 'fdd4159d0389284b15e33c8c80018700b0a8f5c0'

# **
# ** flicker clave
# ** 75b8452aae39dc0967a42c37c139e8a0
# ** flicker secreto
# ** 15075131b9983f9b
# ** Cuenta: graffitisweb@gmail.com
# ** Pass: graffitigraffiti
# ** user_id: 191270823@N05



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
    path('html/nuevapublicacion/publicar', crear_publicacion, name='crear-publicacion'),
    path('html/usuarios', usuarios_list, name='usuarios-list'),
    path('html/usuarios/detalles/<str:pk>/', usuarios_detail, name='usuarios-detail'),
    path('ajax/eventos', cargar_eventos_ajax, name='cargar-eventos-ajax'),
    path('ajax/eventos/<int:ID_ACTIVIDAD>/', cargar_evento_id_ajax, name='cargar-eventos-id'),
    path('html/publicaciones/eliminar/<str:pk>', eliminar_publicacion, name='publicacion-delete'),
    path('html/publicaciones/editar/<str:pk>/<str:gpk>', editar_publicacion, name='editar-publicacion'),
    path('html/publicaciones/detalles/<str:pk>/comentarios', crear_comentario, name='crear-comentario'),
    path('html/publicaciones/detalles/<str:ppk>/graffitis/<str:gpk>/delete', eliminar_graffiti, name='graffiti-delete'),
    path('html/publicaciones/detalles/<str:pk>/comentarios/<str:cpk>', delete_comentario, name='delete-comentario'),
    path('html/publicaciones/detalles/<str:pk>/like', like_publicacion, name='publicacion-like'),
    path('html/inicio/<str:pk>/like', like_inicio, name='inicio-like'),
    path('html/usuarios/detalles/<str:pk>/follow/', usuario_follow, name='usuario-follow'),
    path('html/publicacion/<str:pk>/graffiti/', graffiti_form, name='graffiti-form'),
    path('html/politica-de-privacidad/', privacidad, name='privacidad')
]

#Acciones
urlpatterns += [
    path('loginIn', action_login, name='action_login'),
    path('loginOut', action_logout, name='action_logout')
]